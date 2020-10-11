import pickle
import os.path
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from pathlib import Path

from email.mime.multipart import MIMEMultipart
import mimetypes
from apiclient import errors
from credential.gmail_credential import get_credential
from docopt import docopt
import logging

logger = logging.getLogger(__name__)


def create_message(sender, to, subject, message_text, cc=None):
    enc = "utf-8"
    message = MIMEText(message_text.encode(enc), _charset=enc)
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    if cc:
        message["Cc"] = cc
    encode_message = base64.urlsafe_b64encode(message.as_bytes())
    return {"raw": encode_message.decode()}

def send_message(service, user_id, message):
    try:
        sent_message = (
            service.users().messages().send(userId=user_id, body=message).execute()
        )
        logger.info("Message Id: %s" % sent_message["id"])
        return None
    except errors.HttpError as error:
        logger.info("An error occurred: %s" % error)
        raise error


def main(sender, to, subject, message_text, cc=None):

    creds = get_credential(role="sender")
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    print("sender", sender)
    message = create_message(
            sender, to, subject, message_text, cc=cc
        )
    send_message(service, "me", message)


if __name__ == "__main__":
    args = sys.argv
    sender = args[1]
    to = args[2]
    subject = args[3]
    message_text_file_path = "mails/message.txt"

    #logging.basicConfig(level=logging.DEBUG)

    with open(message_text_file_path, "r", encoding="utf-8") as fp:
        message_text = fp.read()

    main(
        sender=sender,
        to=to,
        subject=subject,
        message_text=message_text,
    )
