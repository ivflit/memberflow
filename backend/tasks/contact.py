from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


CONTACT_EMAIL = 'ivanflitcroft@gmail.com'


@shared_task(bind=True, max_retries=3)
def send_contact_email(self, name: str, email: str, message: str, submitted_at: str):
    try:
        subject = f'New MemberFlow Enquiry from {name}'
        body = (
            f'Name: {name}\n'
            f'Email: {email}\n'
            f'Submitted: {submitted_at}\n\n'
            f'Message:\n{message}'
        )
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [CONTACT_EMAIL])
    except Exception as exc:
        countdown = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)
