import base64
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import tempfile
from tenacity import retry, stop_after_attempt, wait_exponential


class EmailHandler:
    def __init__(self, service):
        self.service = service

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Ensure logs directory exists
        if not os.path.exists('logs'):
            os.makedirs('logs')

        # Add file handler for logging
        fh = logging.FileHandler('logs/email_handler.log')
        fh.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(fh)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def list_messages(self, query: str = None) -> List[Dict]:
        """
        List messages from Gmail that match the query.
        Returns list of message dictionaries with 'id' and 'threadId'.
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query if query else ''
            ).execute()

            messages = results.get('messages', [])
            self.logger.info(f"Found {len(messages)} messages matching query: {query}")
            return messages
        except Exception as e:
            self.logger.error(f"Error listing messages: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_message(self, msg_id: str) -> Dict:
        """Get full message details by message ID."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            return message
        except Exception as e:
            self.logger.error(f"Error getting message {msg_id}: {str(e)}")
            raise

    def get_attachments(self, message: Dict) -> List[Tuple[str, bytes]]:
        """
        Extract attachments from a message.
        Returns list of tuples (filename, file_data).
        """
        attachments = []
        if 'parts' not in message['payload']:
            return attachments

        for part in message['payload']['parts']:
            if part.get('filename'):
                try:
                    attachment = self._process_attachment(message['id'], part)
                    if attachment:
                        attachments.append((part['filename'], attachment))
                except Exception as e:
                    self.logger.error(f"Error processing attachment: {str(e)}")

        return attachments

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _process_attachment(self, message_id: str, part: Dict) -> Optional[bytes]:
        """Process and download a single attachment."""
        try:
            if 'data' in part['body']:
                data = part['body']['data']
            else:
                att_id = part['body']['attachmentId']
                att = self.service.users().messages().attachments().get(
                    userId='me',
                    messageId=message_id,
                    id=att_id
                ).execute()
                data = att['data']
            return base64.urlsafe_b64decode(data.encode('UTF-8'))
        except Exception as e:
            self.logger.error(f"Error processing attachment: {str(e)}")
            raise

    def send_email(self, to: str, subject: str, body: str,
                   attachments: List[Tuple[str, bytes]] = None) -> bool:
        """
        Send an email with optional attachments.
        attachments should be a list of tuples (filename, file_data)
        """
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject

            msg = MIMEText(body)
            message.attach(msg)

            if attachments:
                for filename, file_data in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file_data)
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {filename}'
                    )
                    message.attach(part)

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            self.logger.info(f"Email sent successfully to {to}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False

    def mark_as_read(self, msg_id: str) -> bool:
        """Mark a message as read by removing UNREAD label."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            self.logger.error(f"Error marking message as read: {str(e)}")
            return False

    def save_attachment_to_temp(self, attachment_data: bytes,
                                filename: str) -> str:
        """Save attachment to temporary file and return the path."""
        try:
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, filename)

            with open(temp_path, 'wb') as f:
                f.write(attachment_data)

            self.logger.info(f"Attachment saved to temporary file: {temp_path}")
            return temp_path
        except Exception as e:
            self.logger.error(f"Error saving attachment to temp file: {str(e)}")
            raise
