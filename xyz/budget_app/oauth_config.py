from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.oauth2 import id_token
from google.auth.transport import requests
from googleapiclient.discovery import build
import os
import json


class GoogleAuth:
    def __init__(self):
        self.client_secrets_file = "secrets/client_secret_608925455483-eoud31q4k57om8j2q697hrch34kf9j4k.apps.googleusercontent.com.json"
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        self.flow = None

    def get_authorization_url(self):
        """Create authorization URL for OAuth2 flow."""
        self.flow = Flow.from_client_secrets_file(
            self.client_secrets_file,
            scopes=self.scopes,
            redirect_uri='http://localhost:5000/oauth2callback'
        )

        authorization_url, state = self.flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )

        return authorization_url, state

    def handle_oauth2callback(self, callback_url):
        """Handle the OAuth2 callback and return credentials."""
        try:
            self.flow.fetch_token(authorization_response=callback_url)
            return self.flow.credentials
        except Exception as e:
            raise Exception(f"Error handling OAuth callback: {e}")

    def save_credentials(self, credentials):
        """Save credentials to a file."""
        creds_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

        os.makedirs('data', exist_ok=True)
        with open('data/credentials.json', 'w') as f:
            json.dump(creds_data, f)

    def load_credentials(self):
        """Load credentials from file."""
        try:
            with open('data/credentials.json', 'r') as f:
                creds_data = json.load(f)
            return Credentials(**creds_data)
        except Exception:
            return None

    def build_service(self):
        """Build and return the Gmail service."""
        credentials = self.flow.credentials if self.flow else self.load_credentials()
        if not credentials or not credentials.valid:
            return None
        return build('gmail', 'v1', credentials=credentials)