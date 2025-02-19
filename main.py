import imaplib
import email
import os
import datetime
import smtplib
from email.mime.text import MIMEText

EMAIL=os.environ.get("EMAIL")
PASSWORD=os.environ.get("PASSWORD") 
IMAP_SERVER=os.environ.get("IMAP_SERVER")


def login():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")
    return mail

def logout(mail):
    mail.close()
    mail.logout()

def get_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                break  # Get only the first text/plain part
    else:
        body = msg.get_payload(decode=True).decode()
    return body


def check_email(mail):
    _, data = mail.search(None, "UNSEEN")
    if data == [b'']:
        print("No new emails")
        today = datetime.date.today().strftime("%d-%b-%Y") # 01-Jan-2021
        _, data = mail.search(None, f'SINCE "{today}"') # Get all emails since today

        # return []
    mail_ids = data[0].split()
    all_data = []
    for mail_id in mail_ids:
        _, msg_data = mail.fetch(mail_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = msg["subject"]
                sender = msg["from"]
                body = get_email_body(msg)
            
                Data_in_email = f"From: {sender}\nSubject: {subject}\n Body: {body}\n\n"
                print(Data_in_email)
                all_data.append(Data_in_email)

    
    return all_data

def send_email(to, subject, body):
    msg = MIMEText(body)
    msg["From"] = EMAIL
    msg["To"] = to
    msg["Subject"] = subject

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL, PASSWORD)
    server.sendmail(EMAIL, to, msg.as_string())
    server.quit()

    print("Email sent!")


mail = login()
Data = check_email(mail)
Data_list = Data.split("\n")
sender_email = Data_list[0]
sender_data  = "\n".join(Data_list[1:])

# implement Agent logi here

# use Schedule utility to get schedule data

# send email
logout(mail)
send_email(sender_email, "Hello!", "This is a test email....")


