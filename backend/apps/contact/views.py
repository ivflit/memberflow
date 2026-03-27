import datetime
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from apps.contact.serializers import ContactSerializer
from tasks.contact import send_contact_email


RATE_LIMIT = 3
RATE_WINDOW = 3600  # 1 hour in seconds


class ContactView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # Honeypot check — silent 200 if filled
        if request.data.get('website', ''):
            return Response({'detail': "Thanks! We'll be in touch soon."})

        # Rate limiting by IP
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        cache_key = f'contact_rate:{ip}'
        count = cache.get(cache_key, 0)
        if count >= RATE_LIMIT:
            return Response(
                {'detail': 'Too many requests. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        serializer = ContactSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Increment rate limit counter
        cache.set(cache_key, count + 1, timeout=RATE_WINDOW)

        # Queue email task
        send_contact_email.delay(
            name=serializer.validated_data['name'],
            email=serializer.validated_data['email'],
            message=serializer.validated_data['message'],
            submitted_at=datetime.datetime.utcnow().isoformat(),
        )

        return Response({'detail': "Thanks! We'll be in touch soon."})
