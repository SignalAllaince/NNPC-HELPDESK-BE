import requests
import jwt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(sender_email, subject, content):
    # recipient_name = 'Uchenna Nnamani'
    # content = 'test - I need help with my account'
    # Azure AD application information
    tenant_id = os.environ.get('TENANT_ID')
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET') 
    resource = 'https://graph.microsoft.com'  # Microsoft Graph API
    # sender_email = 'helpdesk@nnpcgroup.com'
    # sender_email = 'unnamani@saconsulting.ai'
    # Uchenna.Nnamani@nnpcgroup.com
    # Benjamin.Busari@nnpcgroup.com
    # Request an access token
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'resource': resource
    }

    token_response = requests.post(token_url, data=token_data)
    access_token = token_response.json().get('access_token')

    # Use the access token to make authenticated requests to Microsoft Graph API
    # Example: Send an email using Microsoft Graph API
    graph_api_url = f'https://graph.microsoft.com/v1.0/users/{sender_email}/sendMail'
    # content = payload.get('Content', '')
    recipient_email = 'unnamani@saconsulting.ai'
    # Create the email message
    msg = MIMEMultipart()
    msg['Subject'] = f'Request for Ticket Escalation'
    msg['From'] = sender_email  # Replace with the sender's email address
    msg['To'] = recipient_email
    body = f"Hello, I have requested for this ticket to be escalated by the serice desk bot. Here are the details:\n\n" \
           f"{content}\n\nRegards,\nAServiceDeskBot"
    msg.attach(MIMEText(body, 'plain'))

    # Send the email using Microsoft Graph API
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    email_data = {
        'message': {
            'subject': msg['Subject'],
            'body': {
                'contentType': 'Text',
                'content': body
            },
            'toRecipients': [
                {
                    'emailAddress': {
                        'address': recipient_email
                    }
                }
            ]
        }
    }

    response = requests.post(graph_api_url, headers=headers, json=email_data)
    if response.status_code == 202:
        return "Email sent successfully"
    else:
        return f"Email could not be sent. Status Code: {response.status_code}", response.text
        # print(response.text)

# Call the function to send the email
# send_email('helpdesk@nnpcgroup.com','test - I need help with my account', 'Uchenna Nnamani')