import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
import logging
from datetime import datetime, timedelta
from flask import Flask, redirect, request, url_for, jsonify, render_template, session
from flask_session import Session
from oauth_config import GoogleAuth
from email_handler import EmailHandler
from budget import PaystubProcessor
import schedule
import threading
import time
from typing import Dict, Optional, List
import json
import secrets
from functools import wraps
import google.oauth2.credentials
import google.auth.transport.requests

# Global variables
auth = GoogleAuth()
email_handler: Optional[EmailHandler] = None
global_credentials = None
paystub_processor = PaystubProcessor(output_file="financial_master.xlsx")

app = Flask(__name__,
    static_folder='static',  # Put your static files in a 'static' folder
    template_folder='templates'  # Put your HTML templates in a 'templates' folder
)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/tmp/flask_session'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
PROCESSED_EMAILS_FILE = 'data/processed_emails.json'
PAYSTUB_DATA_FILE = 'data/paystub_history.json'


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        global email_handler

        if 'credentials' not in session:
            logger.warning("No credentials found in session")
            return redirect(url_for('login'))

        try:
            credentials = google.oauth2.credentials.Credentials(**session['credentials'])

            # Refresh credentials if needed
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(google.auth.transport.requests.Request())
                session['credentials'] = credentials_to_dict(credentials)

            # Reinitialize email handler if it's None
            if email_handler is None:
                gmail_service = auth.build_service(credentials)
                email_handler = EmailHandler(gmail_service)
                logger.info("Reinitialized email handler")

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return redirect(url_for('login'))

    return decorated


def credentials_to_dict(credentials):
    """Convert credentials to dictionary format."""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


def ensure_email_handler():
    """Ensure email handler is initialized"""
    global email_handler, auth

    try:
        if email_handler is None:
            service = auth.build_service()
            if service is None:
                logger.warning("Could not build Gmail service")
                return False
            email_handler = EmailHandler(service)
            logger.info("Email handler initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize email handler: {str(e)}")
        return False


def ensure_data_directory():
    """Ensure data directory exists and create if not."""
    os.makedirs('data', exist_ok=True)
    for file_path in [PROCESSED_EMAILS_FILE, PAYSTUB_DATA_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump([], f)


def load_processed_emails():
    """Load the list of processed email IDs from file."""
    try:
        with open('data/processed_emails.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_processed_emails(processed_emails):
    """Save the list of processed email IDs to file."""
    os.makedirs('data', exist_ok=True)
    with open('data/processed_emails.json', 'w') as f:
        json.dump(processed_emails, f)


def save_paystub_data(paystub_data: Dict):
    """Save processed paystub data to history."""
    try:
        with open(PAYSTUB_DATA_FILE, 'r') as f:
            history = json.load(f)

        paystub_data['processed_date'] = datetime.now().isoformat()
        history.append(paystub_data)

        with open(PAYSTUB_DATA_FILE, 'w') as f:
            json.dump(history, f)
    except Exception as e:
        logger.error(f"Error saving paystub data: {e}")


def process_paystub_emails():
    """Process new paystub emails."""
    global email_handler, paystub_processor

    try:
        if not ensure_email_handler():
            logger.warning("Email handler not properly initialized")
            return {'status': 'error', 'message': 'Email handler not initialized'}

        processed_emails = load_processed_emails()
        query = "subject:paystub has:attachment"

        messages_response = email_handler.list_messages(query=query)
        if not messages_response:
            logger.info("No messages found matching query")
            return {'status': 'success', 'message': 'No new paystubs found'}

        logger.info(f"Found {len(messages_response)} messages matching query")

        results = []
        for msg_data in messages_response:
            try:
                msg_id = msg_data.get('id')
                if not msg_id:
                    logger.warning("Message data missing ID")
                    continue

                logger.info(f"Processing message ID: {msg_id}")

                if msg_id in processed_emails:
                    logger.info(f"Skipping already processed message: {msg_id}")
                    continue

                full_message = email_handler.get_message(msg_id)
                if not full_message:
                    logger.warning(f"Could not fetch full message for ID: {msg_id}")
                    continue

                attachments = email_handler.get_attachments(full_message)
                if not attachments:
                    logger.info(f"No attachments found for message: {msg_id}")
                    continue

                logger.info(f"Found {len(attachments)} attachments for message {msg_id}")

                for attachment in attachments:
                    if isinstance(attachment, tuple) and len(attachment) >= 2:
                        filename, file_data = attachment[:2]
                        if filename.lower().endswith('.pdf'):
                            logger.info(f"Processing PDF attachment: {filename}")

                            # Process the PDF using PaystubProcessor
                            try:
                                paystub_data = paystub_processor.process_pdf(file_data)
                                if paystub_data:
                                    # Save processed data
                                    paystub_processor.save_to_excel(paystub_data)
                                    save_paystub_data(paystub_data)

                                    processed_emails.append(msg_id)
                                    results.append({
                                        'message_id': msg_id,
                                        'filename': filename,
                                        'status': 'processed'
                                    })
                                else:
                                    logger.warning(f"No data extracted from PDF: {filename}")
                            except Exception as pdf_error:
                                logger.error(f"Error processing PDF {filename}: {str(pdf_error)}")
                    else:
                        logger.warning(f"Unexpected attachment format for message {msg_id}")

            except Exception as msg_error:
                logger.error(f"Error processing individual message: {str(msg_error)}")
                continue

        save_processed_emails(processed_emails)

        logger.info(f"Successfully processed {len(results)} new paystubs")
        return {
            'status': 'success',
            'processed': results,
            'total_found': len(messages_response),
            'total_processed': len(results)
        }

    except Exception as e:
        error_msg = f"Error in process_paystub_emails: {str(e)}"
        logger.error(error_msg)
        return {'status': 'error', 'message': error_msg}

def run_scheduled_task():
    """Wrapper for scheduled task to handle any errors."""
    try:
        process_paystub_emails()
    except Exception as e:
        logger.error(f"Error in scheduled task: {e}")


def schedule_processor():
    """Run the email processor on a schedule."""
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")
            time.sleep(60)  # Wait before retrying


@app.route('/')
def index():
    """Render the main page."""
    authenticated = 'credentials' in session
    return render_template('index.html', authenticated=authenticated)


@app.route('/check_auth_status')
def check_auth_status():
    return jsonify({
        'authenticated': 'credentials' in session,
        'email': session.get('email', None)
    })


@app.route('/start_processing')
@requires_auth
def start_processing():
    """Manually trigger email processing."""
    try:
        process_paystub_emails()
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error starting processing: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/get_paystub_history')
@requires_auth
def get_paystub_history():
    """Get processed paystub history."""
    try:
        with open(PAYSTUB_DATA_FILE, 'r') as f:
            history = json.load(f)
        return jsonify(history)
    except Exception as e:
        logger.error(f"Error getting paystub history: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/process_paystubs')
def process_paystubs_route():
    """Route to handle paystub processing request"""
    try:
        if not ensure_email_handler():
            return jsonify({
                'status': 'error',
                'message': 'Email handler not initialized'
            }), 500

        result = process_paystub_emails()

        # Assuming result contains the processed data
        return jsonify({
            'status': 'success',
            'message': 'Paystubs processed successfully',
            'data': result
        })
    except Exception as e:
        logger.error(f"Error processing paystubs: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/get_financial_data')
def get_financial_data():
    try:
        # Read the Excel file
        df = pd.read_excel('financial_master.xlsx')

        # Convert DataFrame to dictionary
        data = {
            'headers': df.columns.tolist(),
            'rows': df.to_dict('records')
        }

        return jsonify({
            'status': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/get_processing_history')
def get_processing_history():
    """Route to get the history of processed emails"""
    try:
        processed_emails = load_processed_emails()
        return jsonify({'processed_emails': processed_emails})
    except Exception as e:
        logger.error(f"Error getting processing history: {e}")
        return jsonify({'error': str(e)}), 500



@app.route('/login')
def login():
    """Initiate the OAuth2 login flow."""
    try:
        authorization_url, state = auth.get_authorization_url()
        session['oauth_state'] = state
        return redirect(authorization_url)
    except Exception as e:
        logger.error(f"Error initiating OAuth flow: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/oauth2callback')
def oauth2callback():
    """Handle the OAuth2 callback."""
    global email_handler, global_credentials
    try:
        if 'oauth_state' not in session:
            return 'No state found in session', 400

        callback_state = request.args.get('state')
        if session['oauth_state'] != callback_state:
            return 'State verification failed', 400

        # Get credentials and store them
        credentials = auth.handle_oauth2callback(request.url)
        session['credentials'] = credentials_to_dict(credentials)
        global_credentials = credentials

        # Save credentials for background tasks
        auth.save_credentials(credentials)

        # Initialize the email handler using the auth's build_service
        service = auth.build_service()
        if service is None:
            raise Exception("Failed to build Gmail service")
        email_handler = EmailHandler(service)

        # Get user email for session
        try:
            profile = service.users().getProfile(userId='me').execute()
            session['email'] = profile.get('emailAddress')
        except Exception as e:
            logger.warning(f"Could not fetch user email: {e}")

        session.pop('oauth_state', None)
        logger.info("Successfully authenticated and initialized email handler")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/logout')
def logout():
    """Clear the session and logout user."""
    global global_credentials, email_handler
    session.clear()
    global_credentials = None
    email_handler = None
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Page not found'}), 404


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


@app.after_request
def after_request(response):
    session.modified = True
    return response


@app.before_request
def before_request():
    if 'credentials' in session:
        logger.debug("Credentials found in session")
        if email_handler:
            logger.debug("Email handler is initialized")
        else:
            logger.debug("Email handler is None")
    else:
        logger.debug("No credentials in session")


def initialize_app():
    """Initialize the application."""
    ensure_data_directory()

    # Schedule email processing
    schedule.every(1).minute.do(run_scheduled_task)

    # Start scheduler in a separate thread
    scheduler_thread = threading.Thread(target=schedule_processor)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Initialize global variables
    global email_handler, global_credentials
    email_handler = None
    global_credentials = None


if __name__ == '__main__':
    initialize_app()
    app.run(host='0.0.0.0', port=5000, debug=True)