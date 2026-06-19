from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


class EmailService:
    
    def __init__(self, default_template: str = 'email_warning.html'):
        self.subject_prefix = "[FPT.AI - MCredit]"
        self.date_format: str = settings.DATE_FORMAT
        self.default_template = default_template
        self.from_mail: str = settings.DEFAULT_FROM_EMAIL
        
       
    def send_email(self, subject: str, recipient_list: list, **kwargs):
        
        mail_data = kwargs.get("data", {})
        template = kwargs.get("template", self.default_template)
        cc_email = kwargs.get("cc_email", [])
        attachment = kwargs.get("attachment", None)
        
        html_message = render_to_string(template, mail_data)

        full_subject = f"{self.subject_prefix} - {subject}"

        email = EmailMessage(
            full_subject,
            html_message,
            self.from_mail,
            recipient_list,
            cc=cc_email
        )

        email.content_subtype = "html"
        if attachment:
            email.attach_file(attachment)

        email.send()

