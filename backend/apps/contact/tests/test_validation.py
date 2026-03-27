import pytest
from unittest.mock import patch, MagicMock
import dns.resolver
from django.test import RequestFactory
from django.core.cache import cache
from apps.contact.serializers import ContactSerializer, _check_mx
from apps.contact.views import ContactView


class TestMXValidation:
    def test_valid_domain_passes(self):
        with patch('dns.resolver.resolve') as mock_resolve:
            mock_resolve.return_value = [MagicMock()]
            assert _check_mx('user@example.com') is True

    def test_nonexistent_domain_fails(self):
        with patch('dns.resolver.resolve') as mock_resolve:
            mock_resolve.side_effect = dns.resolver.NXDOMAIN
            assert _check_mx('user@fakeDomain123notreal.com') is False

    def test_dns_timeout_fails_open(self):
        with patch('dns.resolver.resolve') as mock_resolve:
            mock_resolve.side_effect = dns.resolver.Timeout
            assert _check_mx('user@example.com') is True

    def test_no_answer_fails_open(self):
        with patch('dns.resolver.resolve') as mock_resolve:
            mock_resolve.side_effect = dns.resolver.NoAnswer
            assert _check_mx('user@example.com') is True


class TestContactSerializer:
    def _valid_data(self, **overrides):
        data = {
            'name': 'Ivan Flitcroft',
            'email': 'ivan@example.com',
            'message': 'This is a test message that is long enough.',
            'website': '',
        }
        data.update(overrides)
        return data

    def test_valid_data_passes(self):
        with patch('apps.contact.serializers._check_mx', return_value=True):
            s = ContactSerializer(data=self._valid_data())
            assert s.is_valid(), s.errors

    def test_name_too_short_fails(self):
        with patch('apps.contact.serializers._check_mx', return_value=True):
            s = ContactSerializer(data=self._valid_data(name='A'))
            assert not s.is_valid()
            assert 'name' in s.errors

    def test_name_numbers_only_fails(self):
        with patch('apps.contact.serializers._check_mx', return_value=True):
            s = ContactSerializer(data=self._valid_data(name='12345'))
            assert not s.is_valid()
            assert 'name' in s.errors

    def test_invalid_email_format_fails(self):
        with patch('apps.contact.serializers._check_mx', return_value=True):
            s = ContactSerializer(data=self._valid_data(email='notanemail'))
            assert not s.is_valid()
            assert 'email' in s.errors

    def test_nonexistent_domain_fails(self):
        with patch('apps.contact.serializers._check_mx', return_value=False):
            s = ContactSerializer(data=self._valid_data(email='user@fakeDomain123.com'))
            assert not s.is_valid()
            assert 'email' in s.errors
            assert "doesn't appear to exist" in s.errors['email'][0]

    def test_message_too_short_fails(self):
        with patch('apps.contact.serializers._check_mx', return_value=True):
            s = ContactSerializer(data=self._valid_data(message='Too short'))
            assert not s.is_valid()
            assert 'message' in s.errors


@pytest.mark.django_db
class TestContactView:
    def setup_method(self):
        cache.clear()

    def _make_request(self, data):
        factory = RequestFactory()
        request = factory.post(
            '/api/v1/contact/',
            data=data,
            content_type='application/json',
        )
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.tenant = None
        return request

    def test_honeypot_filled_returns_200_silently(self):
        data = {
            'name': 'Bot',
            'email': 'bot@example.com',
            'message': 'Spam message here that is long enough.',
            'website': 'http://spam.com',
        }
        request = self._make_request(data)
        view = ContactView.as_view()
        response = view(request)
        assert response.status_code == 200
        assert response.data['detail'] == "Thanks! We'll be in touch soon."

    @patch('apps.contact.views.send_contact_email')
    def test_honeypot_filled_task_not_called(self, mock_task):
        data = {
            'name': 'Bot',
            'email': 'bot@example.com',
            'message': 'Spam message here that is long enough.',
            'website': 'http://spam.com',
        }
        request = self._make_request(data)
        ContactView.as_view()(request)
        mock_task.delay.assert_not_called()

    @patch('apps.contact.views.send_contact_email')
    @patch('apps.contact.serializers._check_mx', return_value=True)
    def test_rate_limit_blocks_4th_submission(self, mock_mx, mock_task):
        mock_task.delay = MagicMock()
        data = {
            'name': 'Ivan Flitcroft',
            'email': 'ivan@example.com',
            'message': 'This is a test message that is long enough to pass validation.',
            'website': '',
        }
        view = ContactView.as_view()
        for _ in range(3):
            request = self._make_request(data)
            response = view(request)
            assert response.status_code == 200

        request = self._make_request(data)
        response = view(request)
        assert response.status_code == 429
        assert 'Too many requests' in response.data['detail']
