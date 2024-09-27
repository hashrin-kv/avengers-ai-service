import base64
import os
import shutil
import env_loader
from fastapi import FastAPI, File, HTTPException, UploadFile
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.message import EmailMessage
from insurance.process import summarize

app = FastAPI()

# Scopes for Gmail API
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

# Set up the path for the credentials JSON file
CREDENTIALS_FILE = env_loader.get_environment_variable("CREDENTIALS_FILE")
TOKEN_FILE = env_loader.get_environment_variable("TOKEN_FILE")

def authenticate_gmail():
    """Authenticate and return the Gmail API service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If there are no valid credentials, request the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def process_new_email():
    """Fetch the latest email and save attachments."""
    try:
        service = authenticate_gmail()

        # Get the latest email from inbox
        results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], maxResults=1)
            .execute()
        )
        messages = results.get("messages", [])

        if not messages:
            return {"message": "No emails found."}

        latest_email = messages[0]
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=latest_email["id"], format="full")
            .execute()
        )

        # Define the directory to save attachments
        ATTACHMENT_DIR = "received_attachments"

        if os.path.exists(ATTACHMENT_DIR):
            shutil.rmtree(ATTACHMENT_DIR)
        
        # Create the directory if it doesn't exist
        os.makedirs(ATTACHMENT_DIR, exist_ok=True)

        # Check for attachments in the email
        if "payload" in msg:
            parts = msg["payload"].get("parts", [])
            for part in parts:
                if part.get("filename") and part["body"].get("attachmentId"):
                    attachment_id = part["body"]["attachmentId"]
                    attachment = (
                        service.users()
                        .messages()
                        .attachments()
                        .get(
                            userId="me", messageId=latest_email["id"], id=attachment_id
                        )
                        .execute()
                    )
                    data = attachment.get("data")
                    if data:
                        # Decode the base64url encoded data
                        attachment_data = base64.urlsafe_b64decode(data.encode("UTF-8"))
                        attachment_name = part["filename"]

                        # Define the full path to save the attachment
                        attachment_path = os.path.join(ATTACHMENT_DIR, attachment_name)

                        # Save the attachment locally
                        with open(attachment_path, "wb") as f:
                            f.write(attachment_data)

        # Process the attachments and generate a summary
        summary, summary_email_attachments_path = summarize(ATTACHMENT_DIR)

        # Extract sender's email
        sender = None
        if "payload" in msg and "headers" in msg["payload"]:
            for header in msg["payload"]["headers"]:
                if header["name"] == "From":
                    sender = header["value"]
                    break
        if sender.find("<") != -1:
            sender = sender.split("<")[1].split(">")[0]
        subject = "AI-generated Summary | Medical Reports"

        # Reply back to sender of latest inbox email with the summary and its attachments
        print(sender)
        send_email(sender, subject, summary, summary_email_attachments_path)
        
        if os.path.exists(summary_email_attachments_path):
            shutil.rmtree(summary_email_attachments_path)

        if os.path.exists(ATTACHMENT_DIR):
            shutil.rmtree(ATTACHMENT_DIR)
        
        return {"status": "SUCCESS"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def send_email(to: str, subject: str, body: str, folder_path: str):
    """Send an email with attachments from a local folder."""
    try:
        service = authenticate_gmail()

        # Create the email message without attachments first
        message = EmailMessage()
        message.set_content(body)

        # add attachments to email in the provided folder_path, if any
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    with open(file_path, "rb") as f:
                        attachment_data = f.read()
                        message.add_attachment(attachment_data, maintype='application', subtype=(file_path.split('.')[1]), filename=filename)

        message['To'] = to
        message['From'] = 'me'
        message['Subject'] = subject
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {
            'raw': encoded_message
        }

        # send email
        service.users().messages().send(userId="me", body=create_message).execute()
        return {"message": "Email sent successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
