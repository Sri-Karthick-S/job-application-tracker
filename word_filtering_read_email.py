import imaplib
import json
import email
from email.header import decode_header
from datetime import datetime, timedelta

# Word based filtering

# Load credentials from JSON file
def load_credentials(file_path):
    with open(file_path, 'r') as file:
        credentials = json.load(file)
    return credentials['email'], credentials['password']

# Decode email subject and headers
def decode_mime_words(s):
    return ''.join(
        word.decode(encoding or 'utf-8') if isinstance(word, bytes) else word
        for word, encoding in decode_header(s)
    )

# Fetch and parse emails within a date range and related to job applications
def fetch_job_related_emails(mail, start_date=None, end_date=None):
    # Set default dates if none provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%d-%b-%Y")
    if not end_date:
        end_date = datetime.now().strftime("%d-%b-%Y")

    print(f"Fetching job-related emails from {start_date} to {end_date}...")

    # Search emails in the date range
    status, messages = mail.search(None, f'(SINCE {start_date} BEFORE {end_date})')
    email_ids = messages[0].split()

    if not email_ids:
        print("No emails found in the specified date range!")
        return

    print(f"Found {len(email_ids)} email(s) from the specified date range.\nFiltering job-related emails...\n")

    job_keywords = ["applied", "job application", "shortlisted", "interview", "rejected", "career opportunity", "confirmation"]
    job_related_emails = []

    for email_id in email_ids:
        # Fetch the email by ID
        res, msg_data = mail.fetch(email_id, '(RFC822)')
        
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                # Parse email
                msg = email.message_from_bytes(response_part[1])

                # Decode email subject
                subject = decode_mime_words(msg["Subject"] or "")
                # Decode sender
                from_ = decode_mime_words(msg.get("From") or "")
                
                # Get email content
                content = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() in ["text/plain", "text/html"]:
                            content = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                            break
                else:
                    content = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')

                # Check for job-related keywords in subject or content
                if any(keyword.lower() in subject.lower() or keyword.lower() in content.lower() for keyword in job_keywords):
                    job_related_emails.append((subject, from_, content))
                    print(f"Subject: {subject}")
                    print(f"From: {from_}")
                    print(f"Content Preview: {content[:200]}...\n")  # Print the first 200 characters of content

    print(f"Found {len(job_related_emails)} job-related email(s).")

# Main function
def main():
    # Load credentials
    email_user, email_pass = load_credentials('credentials.json')

    # Connect to Gmail using IMAP
    mail = imaplib.IMAP4_SSL('imap.gmail.com')

    # Login with email and app password
    mail.login(email_user, email_pass)

    # Select the inbox
    mail.select('inbox')

    # Ask user for date range
    print("Enter the date range for fetching emails (format: YYYY-MM-DD)")
    start_date = input("Start date (leave blank for default): ").strip()
    end_date = input("End date (leave blank for default): ").strip()

    # Convert user input to IMAP date format
    start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d-%b-%Y") if start_date else None
    end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d-%b-%Y") if end_date else None

    # Fetch and process job-related emails within the date range
    fetch_job_related_emails(mail, start_date, end_date)

    # Close and logout
    mail.close()
    mail.logout()

if __name__ == '__main__':
    main()
