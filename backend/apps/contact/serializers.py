import re
import dns.resolver
from rest_framework import serializers


def _check_mx(email: str) -> bool:
    """Return True if the email domain has MX records. Fails open on timeout."""
    domain = email.split('@')[-1]
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except dns.resolver.NXDOMAIN:
        return False
    except Exception:
        # DNS timeout, NoAnswer, etc. — fail open to avoid blocking real users
        return True


class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    message = serializers.CharField(min_length=20, max_length=5000)
    website = serializers.CharField(required=False, default='', allow_blank=True)

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Please enter your full name.')
        if not re.search(r"[a-zA-Z]", value):
            raise serializers.ValidationError('Please enter your full name.')
        return value

    def validate_email(self, value):
        if not _check_mx(value):
            raise serializers.ValidationError(
                "That email domain doesn't appear to exist. Please check and try again."
            )
        return value

    def validate_message(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError('Message must be at least 20 characters.')
        return value.strip()
