import pytest
from unittest.mock import MagicMock, patch
from gmail_service import GmailService

# Sample mock data
MOCK_INBOX_RESPONSE = {
    'messages': [
        {'id': 'msg1', 'threadId': 't1'},
        {'id': 'msg2', 'threadId': 't2'}
    ]
}

MOCK_SPAM_RESPONSE = {
    'messages': [
        {'id': 'msg3', 'threadId': 't3'}
    ]
}

def test_fetch_recent_emails_success():
    # Mock the entire service build process
    with patch('gmail_service.build') as mock_build:
        # User credentials would be 'fake_token'
        service = GmailService('fake_token')
        
        # Access the mock service object
        mock_service = mock_build.return_value
        
        # Mock list() responses for INBOX and SPAM
        mock_service.users().messages().list().execute.side_effect = [
            MOCK_INBOX_RESPONSE, # 1st call: Inbox
            MOCK_SPAM_RESPONSE   # 2nd call: Spam
        ]

        # Mock batch execution
        # We need to simulate the callback execution logic of BatchHttpRequest
        mock_batch = mock_service.new_batch_http_request.return_value
        
        def mock_batch_execute():
            # Manually trigger callbacks with sample data
            # msg1 (Inbox)
            service.service.new_batch_http_request.call_args[1]['callback'](
                '1', 
                {
                    'id': 'msg1', 
                    'snippet': 'Hello Inbox 1', 
                    'labelIds': ['INBOX'],
                    'payload': {'headers': [
                        {'name': 'Subject', 'value': 'Inbox 1'},
                        {'name': 'From', 'value': 'alice@example.com'},
                        {'name': 'Date', 'value': '2023-01-01'}
                    ]}
                }, 
                None
            )
            # msg3 (Spam)
            service.service.new_batch_http_request.call_args[1]['callback'](
                '3', 
                {
                    'id': 'msg3', 
                    'snippet': 'Spam Offer', 
                    'labelIds': ['SPAM'],
                    'payload': {'headers': [
                        {'name': 'Subject', 'value': 'Spam 1'},
                        {'name': 'From', 'value': 'spammer@example.com'},
                        {'name': 'Date', 'value': '2023-01-02'}
                    ]}
                }, 
                None
            )
            
        mock_batch.execute.side_effect = mock_batch_execute

        # Run the method
        emails = service.fetch_recent_emails(max_results=10)

        # Assertions
        assert len(emails) == 2 # 1 inbox + 1 spam
        
        # Verify Inbox Email
        inbox_email = next(e for e in emails if e['id'] == 'msg1')
        assert inbox_email['subject'] == 'Inbox 1'
        assert inbox_email['status'] == 'clean'
        assert inbox_email['folder'] == 'Inbox'
        
        # Verify Spam Email
        spam_email = next(e for e in emails if e['id'] == 'msg3')
        assert spam_email['subject'] == 'Spam 1'
        assert spam_email['status'] == 'blocked'
        assert spam_email['folder'] == 'Spam'

def test_fetch_recent_emails_empty():
    with patch('gmail_service.build') as mock_build:
        service = GmailService('fake_token')
        mock_service = mock_build.return_value
        
        # Return empty lists
        mock_service.users().messages().list().execute.return_value = {}
        
        emails = service.fetch_recent_emails()
        assert emails == []
