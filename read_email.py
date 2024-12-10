import imaplib
import json

# Load credentials from JSON file
def load_credentials(file_path):
    with open(file_path, 'r') as file:
        credentials = json.load(file)
    return credentials['email'], credentials['password']

# Main function
def main():
    # Load credentials
    email, password = load_credentials('credentials.json')

    # Connect to Gmail using IMAP
    mail = imaplib.IMAP4_SSL('imap.gmail.com')

    # Login with email and app password
    mail.login(email, password)

    # Select the inbox
    mail.select('inbox')

    # Search for all emails
    result, data = mail.search(None, 'ALL')
    print("Emails:", data[0])

if __name__ == '__main__':
    main()
