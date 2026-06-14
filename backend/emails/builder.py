from django.conf import settings

from .content import STANDARD_FOOTER


URDU_FONT_STACK = "'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', 'Urdu Typesetting', serif"
LATIN_FONT_STACK = "Arial, Helvetica, sans-serif"
NAVY = '#2E4E90'
GOLD = '#C8A951'


def get_first_name(user) -> str:
    if user.full_name:
        parts = user.full_name.strip().split()
        if parts:
            return parts[0]
    if user.display_name:
        parts = user.display_name.strip().split()
        if parts:
            return parts[0]
    return user.username


def get_email_links() -> dict[str, str]:
    base_url = settings.SITE_BASE_URL.rstrip('/')
    return {
        'withdraw_link': settings.PARTICIPANT_WITHDRAW_URL or f'{base_url}/profile',
        'support_page_link': settings.PARTICIPANT_SUPPORT_URL or base_url,
    }


def build_bilingual_subject(subject_en: str, subject_ur: str) -> str:
    return f'{subject_en} / {subject_ur}'


def _render_paragraphs(paragraphs: list[str], *, greeting: str | None = None) -> str:
    blocks = []
    if greeting:
        blocks.append(f'<p style="margin: 0 0 14px; font-size: 15px; line-height: 1.6;">Dear {greeting},</p>')
    for paragraph in paragraphs:
        blocks.append(
            f'<p style="margin: 0 0 14px; font-size: 15px; line-height: 1.6; color: #3f3f46;">{paragraph}</p>'
        )
    return ''.join(blocks)


def _render_urdu_paragraphs(paragraphs: list[str], *, greeting: str | None = None) -> str:
    blocks = []
    if greeting:
        blocks.append(
            f'<p style="margin: 0 0 14px; font-size: 16px; line-height: 1.9;">محترم {greeting}،</p>'
        )
    for paragraph in paragraphs:
        blocks.append(
            f'<p style="margin: 0 0 14px; font-size: 16px; line-height: 1.9; color: #3f3f46;">{paragraph}</p>'
        )
    return ''.join(blocks)


def build_standard_footer_html(links: dict[str, str]) -> str:
    en_paragraphs = [
        paragraph.format(**links) for paragraph in STANDARD_FOOTER['paragraphs_en']
    ]
    ur_paragraphs = [
        paragraph.format(**links) for paragraph in STANDARD_FOOTER['paragraphs_ur']
    ]

    en_html = ''.join(
        f'<p style="margin: 0 0 10px; font-size: 12px; line-height: 1.5; color: #71717a;">{paragraph}</p>'
        for paragraph in en_paragraphs
    )
    ur_html = ''.join(
        f'<p style="margin: 0 0 10px; font-size: 13px; line-height: 1.8; color: #71717a;">{paragraph}</p>'
        for paragraph in ur_paragraphs
    )

    return f"""
    <hr style="border: 0; border-top: 1px solid #e4e4e7; margin: 24px 0;">
    <div style="font-family: {LATIN_FONT_STACK};">
        {en_html}
    </div>
    <div dir="rtl" style="font-family: {URDU_FONT_STACK}; text-align: right; margin-top: 16px;">
        {ur_html}
    </div>
    """


def build_welcome_email(first_name: str, links: dict[str, str] | None = None) -> dict[str, str]:
    from .content import WELCOME_EMAIL

    links = links or get_email_links()
    subject = build_bilingual_subject(WELCOME_EMAIL['subject_en'], WELCOME_EMAIL['subject_ur'])

    english_body = _render_paragraphs(WELCOME_EMAIL['paragraphs_en'], greeting=first_name)
    english_body += (
        f'<p style="margin: 18px 0 4px; font-size: 15px; line-height: 1.6;">{WELCOME_EMAIL["closing_en"]}</p>'
        f'<p style="margin: 0; font-size: 15px; line-height: 1.6; font-weight: 600;">'
        f'{WELCOME_EMAIL["closing_team_en"]}</p>'
    )

    urdu_body = _render_urdu_paragraphs(WELCOME_EMAIL['paragraphs_ur'], greeting=first_name)
    urdu_body += (
        f'<p style="margin: 18px 0 4px; font-size: 16px; line-height: 1.9;">{WELCOME_EMAIL["closing_ur"]}</p>'
        f'<p style="margin: 0; font-size: 16px; line-height: 1.9; font-weight: 600;">'
        f'{WELCOME_EMAIL["closing_team_ur"]}</p>'
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap" rel="stylesheet">
    </head>
    <body style="margin: 0; padding: 0; background-color: #f4f4f5;">
        <div style="max-width: 600px; margin: 0 auto; padding: 24px 16px;">
            <div style="background-color: #ffffff; border: 1px solid #e4e4e7; border-radius: 8px; padding: 24px;">
                <h1 style="margin: 0 0 18px; font-family: {LATIN_FONT_STACK}; font-size: 22px; color: {NAVY}; border-bottom: 2px solid {GOLD}; padding-bottom: 10px;">
                    {WELCOME_EMAIL['title_en']}
                </h1>
                <div style="font-family: {LATIN_FONT_STACK}; color: #18181b;">
                    {english_body}
                </div>
                <hr style="border: 0; border-top: 1px solid #e4e4e7; margin: 24px 0;">
                <div dir="rtl" style="font-family: {URDU_FONT_STACK}; text-align: right; color: #18181b;">
                    <h2 style="margin: 0 0 18px; font-size: 22px; color: {NAVY}; border-bottom: 2px solid {GOLD}; padding-bottom: 10px;">
                        {WELCOME_EMAIL['title_ur']}
                    </h2>
                    {urdu_body}
                </div>
                {build_standard_footer_html(links)}
            </div>
        </div>
    </body>
    </html>
    """

    text_content = '\n\n'.join([
        WELCOME_EMAIL['subject_en'],
        '',
        f'Dear {first_name},',
        *WELCOME_EMAIL['paragraphs_en'],
        WELCOME_EMAIL['closing_en'],
        WELCOME_EMAIL['closing_team_en'],
        '',
        WELCOME_EMAIL['subject_ur'],
        '',
        f'محترم {first_name}،',
        *WELCOME_EMAIL['paragraphs_ur'],
        WELCOME_EMAIL['closing_ur'],
        WELCOME_EMAIL['closing_team_ur'],
        '',
        STANDARD_FOOTER['paragraphs_en'][0].format(**links),
        STANDARD_FOOTER['paragraphs_en'][1].format(**links),
        STANDARD_FOOTER['paragraphs_en'][2],
        '',
        STANDARD_FOOTER['paragraphs_ur'][0].format(**links),
        STANDARD_FOOTER['paragraphs_ur'][1].format(**links),
        STANDARD_FOOTER['paragraphs_ur'][2],
    ])

    return {
        'subject': subject,
        'text_content': text_content,
        'html_content': html_content,
    }
