import pickle
import base64
import json
import io
import csv
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
from email.mime.text import MIMEText
from apiclient import errors
import logging
from docopt import docopt
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from credential.gmail_credential import get_credential

logger = logging.getLogger(__name__)


def list_labels(service, user_id):
    labels = []
    response = service.users().labels().list(userId=user_id).execute()
    return response["labels"]


def decode_base64url_data(data):
    decoded_bytes = base64.urlsafe_b64decode(data)
    decoded_message = decoded_bytes.decode("UTF-8")
    return decoded_message


def get_message(service, user_id, query, count=1):
    try:
        message_ids = (
            service.users()
            .messages()
            .list(userId=user_id, maxResults=count, q=query, includeSpamTrash=True)
            .execute()
        )

        if message_ids["resultSizeEstimate"] == 0:
            logger.warning("no result data!")
            return []

        for message_id in message_ids["messages"]:
            message_raw = (
                service.users()
                .messages()
                .get(userId="me", id=message_id["id"], format = "raw")
                .execute()
            )

            message_components = (
                service.users()
                .messages()
                .get(userId="me", id=message_id["id"])
                .execute()
            )

            raw_message =  decode_base64url_data(message_raw["raw"])
            message_body = decode_base64url_data(message_components["payload"]["body"]["data"])
            return raw_message, message_body

    except errors.HttpError as error:
        print("An error occurred: %s" % error)


def main(query, message_file_path):
    creds = get_credential(role="receiver")
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    # get list of labels
    labels = list_labels(service, "me")
    #target_label_ids = [label["id"] for label in labels if label["name"] == tag]
    #messages = list_message(service, "me", query, target_label_ids, count=count)
    raw_message, message_body = get_message(service, "me", query, count=1)
    #someimplementation
    with open(message_file_path, mode="w") as f:
        f.write(raw_message + '\n\n' + message_body)

    return message_body


if __name__ == "__main__":
    args = sys.argv
    send_from = args[1]
    query="from:"+send_from
    main(query=query, message_save_file_path="mails/inbox/test.eml")
