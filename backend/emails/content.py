"""Participant email copy from Psycheversity_Participant_Emails_Bilingual.docx."""

WELCOME_EMAIL = {
    'subject_en': 'Welcome to Psycheversity : your wellbeing journey begins',
    'subject_ur': 'سائیکیورسٹی میں خوش آمدید : آپ کا بہبود کا سفر شروع',
    'title_en': 'Welcome to Psycheversity',
    'title_ur': 'سائیکیورسٹی میں خوش آمدید',
    'paragraphs_en': [
        'Thank you for joining the Psycheversity wellbeing study. We are glad to have you with us.',
        (
            'Over the coming year you will complete short daily writing exercises in a few phases, '
            'with brief questionnaires along the way. Everything is online and takes only a few minutes a day.'
        ),
        (
            'You will shortly receive your first personal wellbeing summary, based on the questionnaire '
            'you just completed.'
        ),
        (
            'Participation is entirely voluntary. You may stop at any time, for any reason, without giving '
            'a reason and without any penalty.'
        ),
        "During the writing phases we will email you each day with a link to that day's exercise.",
    ],
    'paragraphs_ur': [
        'سائیکیورسٹی کی بہبود تحقیق میں شامل ہونے کا شکریہ۔ ہمیں خوشی ہے کہ آپ ہمارے ساتھ ہیں۔',
        (
            'آنے والے سال کے دوران آپ مختلف مرحلوں میں روزانہ مختصر تحریری مشقیں مکمل کریں گے، '
            'اور بیچ بیچ میں چند مختصر سوالنامے بھی ہوں گے۔ سب کچھ آن لائن ہے اور روزانہ صرف چند منٹ لیتا ہے۔'
        ),
        (
            'آپ کو جلد ہی، آپ کے ابھی مکمل کیے گئے سوالنامے کی بنیاد پر، '
            'آپ کی پہلی ذاتی بہبود رپورٹ موصول ہوگی۔'
        ),
        (
            'اس تحقیق میں شرکت مکمل طور پر رضاکارانہ ہے۔ آپ کسی بھی وقت، کسی بھی وجہ سے، '
            'بغیر وجہ بتائے اور بغیر کسی نقصان کے رُک سکتے ہیں۔'
        ),
        'تحریری مرحلوں کے دوران ہم آپ کو ہر روز ایک ای میل بھیجیں گے جس میں اُس دن کی مشق کا لنک ہوگا۔',
    ],
    'closing_en': 'Warm regards,',
    'closing_team_en': 'Psycheversity Research Team',
    'closing_ur': 'نیک تمناؤں کے ساتھ،',
    'closing_team_ur': 'سائیکیورسٹی ریسرچ ٹیم',
}

STANDARD_FOOTER = {
    'paragraphs_en': [
        (
            'You can withdraw from this study at any time, with no penalty: '
            '<a href="{withdraw_link}" style="color: #2E4E90;">{withdraw_link}</a>.'
        ),
        (
            'If you need support, help is available: '
            '<a href="{support_page_link}" style="color: #2E4E90;">{support_page_link}</a>.'
        ),
        (
            'Psycheversity Research Team : Pakistan Institute of Mind Sciences (PIMS), '
            'in collaboration with Universiti Kebangsaan Malaysia (UKM). support@psycheversity.com'
        ),
    ],
    'paragraphs_ur': [
        'آپ کسی بھی وقت، بغیر کسی نقصان کے اس تحقیق سے دستبردار ہو سکتے ہیں: {withdraw_link}۔',
        'اگر آپ کو مدد درکار ہو تو معاونت دستیاب ہے: {support_page_link}۔',
        (
            'سائیکیورسٹی ریسرچ ٹیم : پاکستان انسٹیٹیوٹ آف مائنڈ سائنسز (PIMS)، '
            'یونیورسٹی کبنگسان ملائیشیا (UKM) کے اشتراک سے۔ support@psycheversity.com'
        ),
    ],
}
