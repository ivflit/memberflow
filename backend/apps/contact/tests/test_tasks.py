import pytest
from unittest.mock import patch, call
from tasks.contact import send_contact_email


class TestSendContactEmail:
    @patch('tasks.contact.send_mail')
    def test_sends_email_with_correct_subject(self, mock_send_mail):
        send_contact_email(
            name='Ivan Flitcroft',
            email='ivan@example.com',
            message='Hello, I would like to set up MemberFlow for my club.',
            submitted_at='2026-03-27T10:00:00',
        )
        args = mock_send_mail.call_args
        assert args[0][0] == 'New MemberFlow Enquiry from Ivan Flitcroft'

    @patch('tasks.contact.send_mail')
    def test_sends_to_correct_recipient(self, mock_send_mail):
        send_contact_email(
            name='Ivan Flitcroft',
            email='ivan@example.com',
            message='Hello, I would like to set up MemberFlow for my club.',
            submitted_at='2026-03-27T10:00:00',
        )
        args = mock_send_mail.call_args
        recipients = args[0][3]
        assert 'ivanflitcroft@gmail.com' in recipients

    @patch('tasks.contact.send_mail')
    def test_body_contains_name_email_message(self, mock_send_mail):
        send_contact_email(
            name='Ivan Flitcroft',
            email='ivan@example.com',
            message='Hello, I would like to set up MemberFlow for my club.',
            submitted_at='2026-03-27T10:00:00',
        )
        body = mock_send_mail.call_args[0][1]
        assert 'Ivan Flitcroft' in body
        assert 'ivan@example.com' in body
        assert 'Hello, I would like to set up MemberFlow' in body
        assert '2026-03-27T10:00:00' in body
