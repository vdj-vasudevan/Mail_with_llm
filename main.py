import imaplib
import email
import os
import datetime
import smtplib
import pandas as pd 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from agent.mail_agent import get_port_pair_data
from Schedule.one import get_one_schedule

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

def send_email_with_df(to, subject, body, df, filename="data.csv"):
    # Save DataFrame to a temporary CSV file
    temp_path = f"/tmp/{filename}"  # Use "data.csv" or specify another name
    df.to_csv(temp_path, index=False)

    # Create the email
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Attach the CSV file
    with open(temp_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    msg.attach(part)

    # Send the email
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL, PASSWORD)
    server.sendmail(EMAIL, to, msg.as_string())
    server.quit()

    # Clean up the temporary file
    os.remove(temp_path)

    print("Email sent with DataFrame as CSV attachment!")

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
Data = check_email(mail)[0]
Data_list = Data.split("\n")
sender_email = Data_list[0].split("<")[1].strip(">")
sender_data  = "\n".join(Data_list[1:])
if "CONDITION TO CHECK":
    send_email(sender_email, "Hello!", "You have Exhausted your free limit to continue kindly Contact the admin : https://github.com/vdj-vasudevan")
# sender_data = "Subject: Get Schedule\nBody: From Shanghai to Hamburg\n\n"
# implement Agent logi here
portpair_list = get_port_pair_data(sender_data, False)

result = []
# use Schedule utility to get schedule data
for portpair in portpair_list:
    origin = portpair["origin_port"]
    destination = portpair["destination_port"]
    op = get_one_schedule(origin, destination)
    result.append(op)


df = pd.DataFrame()
dataframes = []  # Collect DataFrames in a list

for i in range(len(result)):
    if result[i] is None:
        continue
    dataframes.append(pd.DataFrame(result[i]["scheduleLines"]))  # Append to list

if dataframes:
    df = pd.concat(dataframes, ignore_index=True)

df = df.reset_index(drop=True)
# send email

send_email_with_df(sender_email, "Check out the Schedules", "Here is the data you requested.", df)
logout(mail)

# send_email(sender_email, "Hello!", "This is a test email....")



