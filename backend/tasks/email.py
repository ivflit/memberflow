from celery import shared_task
from django.core.mail import send_mail


@shared_task(bind=True, max_retries=3)
def send_invite_email(self, invitation_id, base_url):
    try:
        from apps.users.models import UserInvitation
        invitation = UserInvitation.objects.select_related('organization').get(pk=invitation_id)
        org = invitation.organization
        link = f'{base_url}/auth/set-password?token={invitation.token}&mode=invite'
        subject = f"You've been invited to join {org.name} on MemberFlow"
        body = (
            f"You've been invited to create an account for {org.name}.\n\n"
            f"Click the link below to set your password and complete your registration.\n"
            f"This link expires in 7 days.\n\n"
            f"{link}\n\n"
            f"If you didn't expect this invitation, you can ignore this email."
        )
        send_mail(subject, body, None, [invitation.email])
    except Exception as exc:
        countdown = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


@shared_task(bind=True, max_retries=3)
def send_reset_email(self, token_id, base_url):
    try:
        from apps.users.models import PasswordResetToken
        reset_token = PasswordResetToken.objects.select_related('user__organization').get(pk=token_id)
        org = reset_token.user.organization
        link = f'{base_url}/auth/set-password?token={reset_token.token}&mode=reset'
        subject = f'Reset your MemberFlow password for {org.name}'
        body = (
            f'We received a request to reset the password for your {org.name} account.\n\n'
            f'Click the link below to set a new password.\n'
            f'This link expires in 24 hours and can only be used once.\n\n'
            f'{link}\n\n'
            f"If you didn't request a password reset, you can ignore this email."
        )
        send_mail(subject, body, None, [reset_token.user.email])
    except Exception as exc:
        countdown = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)
