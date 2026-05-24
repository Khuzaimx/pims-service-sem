import csv
import io
import logging
from celery import shared_task
from django.core.files.base import ContentFile
from .models import ExportTask

logger = logging.getLogger(__name__)

@shared_task
def generate_baseline_export_csv(task_id):
    try:
        task = ExportTask.objects.get(id=task_id)
        task.status = 'PROCESSING'
        task.save()

        from questionnaires.models import ResponseSet, Question
        
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        
        # Get ordered questions for the baseline questionnaire to act as columns
        questions = list(Question.objects.filter(questionnaire__is_baseline=True).order_by('order'))

        # Header for Wide Format
        static_headers = ['ParticipantID', 'Username', 'Group', 'DateOfBirth', 'StartedAt', 'CompletedAt']
        dynamic_headers = [f"Question {i + 1}" for i in range(len(questions))]
        writer.writerow(static_headers + dynamic_headers)

        # Optimize DB query: fetch all completed ResponseSets for the baseline questionnaire
        qs = ResponseSet.objects.filter(
            questionnaire__is_baseline=True, 
            status='COMPLETED'
        )

        # Apply filters from task metadata
        group_name = task.filters.get('group')
        if group_name and group_name != 'All':
            qs = qs.filter(user__group__name=group_name)

        response_sets = qs.select_related(
            'user', 'user__group', 'questionnaire'
        ).prefetch_related(
            'responses__question', 'responses__selected_option'
        )

        for rs in response_sets:
            resp_dict = {ans.question_id: ans for ans in rs.responses.all()}
            
            row = [
                rs.user.user_id,
                rs.user.username,
                rs.user.group.name if rs.user.group else 'None',
                rs.user.date_of_birth.strftime('%Y-%m-%d') if rs.user.date_of_birth else '',
                rs.started_at.strftime('%Y-%m-%d %H:%M:%S') if rs.started_at else '',
                rs.completed_at.strftime('%Y-%m-%d %H:%M:%S') if rs.completed_at else '',
            ]
            
            for q in questions:
                ans = resp_dict.get(q.id)
                if ans:
                    if ans.selected_option:
                        row.append(ans.selected_option.label)
                    elif ans.text_value:
                        row.append(ans.text_value.replace('\n', ' '))
                    else:
                        row.append('')
                else:
                    row.append('')
            
            writer.writerow(row)

        # Save the CSV to the FileField
        file_name = f"baseline_export_{task.id}.csv"
        task.file.save(file_name, ContentFile(output.getvalue().encode('utf-8')))
        task.status = 'SUCCESS'
        task.save()
        
    except Exception as e:
        logger.error(f"Error generating baseline export CSV for task {task_id}: {e}")
        try:
            task = ExportTask.objects.get(id=task_id)
            task.status = 'FAILED'
            task.error_message = str(e)
            task.save()
        except Exception as task_update_error:
            logger.error(f"Failed to update task {task_id} status to FAILED: {task_update_error}")
        raise e

@shared_task
def generate_posttest_export_csv(task_id):
    try:
        task = ExportTask.objects.get(id=task_id)
        task.status = 'PROCESSING'
        task.save()

        from questionnaires.models import ResponseSet, Question
        
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        
        questions = list(Question.objects.filter(questionnaire__is_posttest=True).order_by('order'))

        static_headers = ['ParticipantID', 'Username', 'Group', 'DateOfBirth', 'StartedAt', 'CompletedAt']
        dynamic_headers = [f"Question {i + 1}" for i in range(len(questions))]
        writer.writerow(static_headers + dynamic_headers)

        qs = ResponseSet.objects.filter(
            questionnaire__is_posttest=True, 
            status='COMPLETED'
        )

        group_name = task.filters.get('group')
        if group_name and group_name != 'All':
            qs = qs.filter(user__group__name=group_name)

        response_sets = qs.select_related(
            'user', 'user__group', 'questionnaire'
        ).prefetch_related(
            'responses__question', 'responses__selected_option'
        )

        for rs in response_sets:
            resp_dict = {ans.question_id: ans for ans in rs.responses.all()}
            
            row = [
                rs.user.user_id,
                rs.user.username,
                rs.user.group.name if rs.user.group else 'None',
                rs.user.date_of_birth.strftime('%Y-%m-%d') if rs.user.date_of_birth else '',
                rs.started_at.strftime('%Y-%m-%d %H:%M:%S') if rs.started_at else '',
                rs.completed_at.strftime('%Y-%m-%d %H:%M:%S') if rs.completed_at else '',
            ]
            
            for q in questions:
                ans = resp_dict.get(q.id)
                if ans:
                    if ans.selected_option:
                        row.append(ans.selected_option.label)
                    elif ans.text_value:
                        row.append(ans.text_value.replace('\n', ' '))
                    else:
                        row.append('')
                else:
                    row.append('')
            
            writer.writerow(row)

        file_name = f"posttest_export_{task.id}.csv"
        task.file.save(file_name, ContentFile(output.getvalue().encode('utf-8')))
        task.status = 'SUCCESS'
        task.save()
        
    except Exception as e:
        logger.error(f"Error generating posttest export CSV for task {task_id}: {e}")
        try:
            task = ExportTask.objects.get(id=task_id)
            task.status = 'FAILED'
            task.error_message = str(e)
            task.save()
        except Exception as task_update_error:
            logger.error(f"Failed to update task {task_id} status to FAILED: {task_update_error}")
        raise e


@shared_task
def generate_longitudinal_export_csv(task_id):
    import tempfile
    import os
    import re
    from django.core.files import File
    from django.contrib.auth import get_user_model
    from questionnaires.models import Question, ResponseSet, Response

    try:
        task = ExportTask.objects.get(id=task_id)
        task.status = 'PROCESSING'
        task.save()

        # 1. Fetch and configure sociodemographic questions
        socio_questions = list(Question.objects.filter(questionnaire__assessment_type='SOCIODEMOGRAPHIC').order_by('order'))
        for q in socio_questions:
            content_lower = q.content.lower()
            if 'gender' in content_lower:
                header_name = 'Socio_Gender'
            elif 'age' in content_lower:
                header_name = 'Socio_Age'
            elif 'employment' in content_lower:
                header_name = 'Socio_Employment'
            elif 'education' in content_lower:
                header_name = 'Socio_Education'
            else:
                header_name = f"Socio_Q{q.order}"
            q.header_name = header_name

        # 2. Fetch and configure psychometric questions
        psy_questions = list(Question.objects.filter(questionnaire__assessment_type='PSYCHOMETRIC').order_by('order'))

        # 3. Build CSV Headers
        headers = ['ParticipantID', 'Username', 'Group', 'DateOfBirth', 'RegistrationDate', 'BaselineCompletedAt']
        headers += [q.header_name for q in socio_questions]

        # Map tuples of (question_id, milestone) to columns
        psy_columns = []
        milestones = ['SIGNUP', '7_DAYS', '3_MONTHS', '6_MONTHS', '1_YEAR']
        for milestone in milestones:
            for q in psy_questions:
                match = re.match(r'^\[([^\]]+)\]', q.content)
                tag = re.sub(r'[^a-zA-Z0-9\-]', '', match.group(1)).upper() if match else "PSYCH"
                headers.append(f"{tag}_Q{q.order}_{milestone}")
                psy_columns.append((q.id, milestone))

        # 4. Fetch Users
        User = get_user_model()
        users_qs = User.objects.filter(
            is_active=True,
            has_completed_baseline=True
        ).select_related('group').order_by('user_id')

        group_name = task.filters.get('group')
        if group_name and group_name != 'All':
            users_qs = users_qs.filter(group__name=group_name)

        # 5. Write to a Temporary File (O(1) memory overhead)
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, newline='', suffix='.csv', encoding='utf-8') as temp_file:
            writer = csv.writer(temp_file, quoting=csv.QUOTE_ALL)
            writer.writerow(headers)

            for user in users_qs.iterator(chunk_size=1000):
                # Fetch all completed responses for this user in a single optimized query
                responses = Response.objects.filter(
                    response_set__user=user,
                    response_set__status='COMPLETED'
                ).select_related('response_set', 'question', 'selected_option')

                resp_map = {}
                for r in responses:
                    m = r.response_set.milestone
                    if r.response_set.questionnaire.assessment_type == 'SOCIODEMOGRAPHIC':
                        resp_map[r.question_id] = r
                    else:
                        resp_map[(r.question_id, m)] = r

                row = [
                    user.user_id,
                    user.username,
                    user.group.name if user.group else 'None',
                    user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else '',
                    user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
                    user.baseline_completed_at.strftime('%Y-%m-%d %H:%M:%S') if user.baseline_completed_at else '',
                ]

                # Append sociodemographic values
                for q in socio_questions:
                    ans = resp_map.get(q.id)
                    if ans:
                        val = ans.selected_option.label if ans.selected_option else (ans.text_value or '')
                        row.append(val.replace('\n', ' '))
                    else:
                        row.append('')

                # Append psychometric values
                for q_id, milestone in psy_columns:
                    ans = resp_map.get((q_id, milestone))
                    if ans:
                        val = ans.selected_option.label if ans.selected_option else (ans.text_value or '')
                        row.append(val.replace('\n', ' '))
                    else:
                        row.append('')

                writer.writerow(row)

            temp_file_path = temp_file.name

        # 6. Save the temporary file to the Task model
        with open(temp_file_path, 'rb') as f:
            file_name = f"longitudinal_export_{task.id}.csv"
            task.file.save(file_name, File(f))

        task.status = 'SUCCESS'
        task.save()

        # Clean up temporary file
        os.unlink(temp_file_path)

    except Exception as e:
        logger.error(f"Error generating longitudinal export CSV for task {task_id}: {e}")
        try:
            task = ExportTask.objects.get(id=task_id)
            task.status = 'FAILED'
            task.error_message = str(e)
            task.save()
        except Exception as task_update_error:
            logger.error(f"Failed to update task {task_id} status to FAILED: {task_update_error}")
        raise e
