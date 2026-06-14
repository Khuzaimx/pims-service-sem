import logging

from celery import shared_task
from celery.exceptions import Retry
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives

from .builder import build_welcome_email, get_first_name

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_welcome_email_task(self, user_id: int):
    """
    Send the E1 bilingual welcome email after successful onboarding (Day 0).
    Skips disqualified users and screen-out cases (suicide_risk_triggered on SIGNUP).
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error('Welcome email skipped: user %s not found', user_id)
        return {'status': 'skipped', 'reason': 'user_not_found'}

    if not user.email:
        logger.error('Welcome email skipped: user %s has no email', user.username)
        return {'status': 'skipped', 'reason': 'missing_email'}

    if user.is_disqualified:
        logger.info('Welcome email skipped: user %s is disqualified', user.username)
        return {'status': 'skipped', 'reason': 'disqualified'}

    if not user.onboarding_completed_at:
        logger.info('Welcome email skipped: user %s has not completed onboarding', user.username)
        return {'status': 'skipped', 'reason': 'onboarding_incomplete'}

    from questionnaires.models import ResponseSet

    signup_response = (
        ResponseSet.objects.filter(
            user=user,
            milestone='SIGNUP',
            questionnaire__assessment_type='PSYCHOMETRIC',
            status='COMPLETED',
        )
        .order_by('-completed_at')
        .first()
    )
    if signup_response and signup_response.suicide_risk_triggered:
        logger.info(
            'Welcome email skipped: user %s triggered screen-out risk on SIGNUP',
            user.username,
        )
        return {'status': 'skipped', 'reason': 'screen_out_risk'}

    first_name = get_first_name(user)
    email_content = build_welcome_email(first_name)

    msg = EmailMultiAlternatives(
        subject=email_content['subject'],
        body=email_content['text_content'],
        from_email=settings.PARTICIPANT_EMAIL_FROM,
        to=[user.email],
        reply_to=[settings.PARTICIPANT_EMAIL_REPLY_TO],
    )
    msg.attach_alternative(email_content['html_content'], 'text/html')

    try:
        msg.send(fail_silently=False)
        logger.info('Successfully sent welcome email to %s (%s)', user.username, user.email)
        return {'status': 'sent', 'recipient': user.email}
    except Exception as exc:
        logger.error('Error sending welcome email to %s: %s', user.email, exc)
        if isinstance(exc, Retry):
            raise
        raise self.retry(exc=exc) from exc
