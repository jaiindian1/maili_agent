import os
import json
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Access scope required to create, modify, and send emails via Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    """Handles secure OAuth2 authentication with Google APIs."""
    creds = None
    # token.json stores your active session tokens locally once authenticated
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "Error: 'credentials.json' missing. Download it from Google Cloud Console "
                    "and place it right inside your project directory."
                )
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        print(f"Failed to initialize Gmail API client: {e}")
        return None

def create_message(sender, to, subject, message_text):
    """Encodes standard text into the secure MIME format required by Gmail."""
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

def send_email_via_agent(service, user_id, message):
    """Executes the API call to transmit the message."""
    try:
        sent_message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f" Successfully Sent! Message ID: {sent_message['id']}")
        return sent_message
    except HttpError as error:
        print(f" An API error occurred: {error}")
        return None

def load_targets(file_path='targets.json'):
    """Loads target university details dynamically from external JSON."""
    if not os.path.exists(file_path):
        print(f"Error: Target data file '{file_path}' not found.")
        return []
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Error: '{file_path}' contains malformed JSON data.")
        return []

# =====================================================================
# AGENT LOGIC & EXECUTION LOOP
# =====================================================================
def run_email_outreach_agent(user_email):
    """Core executive execution loop for personalized dean outreach."""
    deans_list = load_targets()
    if not deans_list:
        print("No targets available. Aborting run.")
        return

    print("Connecting to secure Gmail Service layer...")
    service = get_gmail_service()
    if not service:
        return

    print(f"\nEngine started. Processing {len(deans_list)} university paths...\n")

    for target in deans_list:
        subject = f"Collaboration Opportunity: AI/ML Initiatives - {target['university']}"
        
        email_body = (
            f"Dear Dean {target['name']},\n\n"
            f"I hope this email finds you well.\n\n"
            f"I am reaching out regarding the cutting-edge developments happening at {target['university']}. "
            f"With extensive experience in business operations and strategic management, combined with "
            f"advanced technical insights in Deep Learning and AI systems engineering, I am keenly interested "
            f"in exploring potential synergies or industry-academic collaborations with your department.\n\n"
            f"I would welcome a brief opportunity to connect and discuss how my practical execution frameworks "
            f"can align with your university's current technical initiatives.\n\n"
            f"Thank you for your time and consideration.\n\n"
            f"Sincerely,\n"
            f"Jai Prakash Thakur"
        )

        # Human-in-the-Loop Safeguard Verification
        print("=" * 60)
        print(f"TARGET DEAN : {target['name']}")
        print(f"UNIVERSITY  : {target['university']}")
        print(f"EMAIL       : {target['email']}")
        print(f"SUBJECT     : {subject}")
        print("-" * 60)
        print(email_body)
        print("=" * 60)
        
        approval = input(f"Approve transmission to Dean {target['name']}? (yes/no): ").strip().lower()
        
        if approval == 'yes':
            print("Encoding payload and pushing to Gmail gateway...")
            raw_msg = create_message(user_email, target['email'], subject, email_body)
            send_email_via_agent(service, 'me', raw_msg)
            print("Ready for next target.\n")
        else:
            print(f"Skipped transmission for {target['name']}.\n")

if __name__ == '__main__':
    # TODO: Replace with your actual authorized Gmail address
    YOUR_EMAIL = "your.email@gmail.com" 
    
    run_email_outreach_agent(YOUR_EMAIL)
