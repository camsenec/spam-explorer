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
from gmail_credential import get_credential

logger = logging.getLogger(__name__)


def list_labels(service, user_id):
    labels = []
    response = service.users().labels().list(userId=user_id).execute()
    return response["labels"]


def decode_base64url_data(data):
    decoded_bytes = base64.urlsafe_b64decode(data)
    decoded_message = decoded_bytes.decode("UTF-8")
    return decoded_message


def list_message(service, user_id, query, label_ids=[], count=3):
    messages = {}
    try:
        message_ids = (
            service.users()
            .messages()
            .list(userId=user_id, maxResults=count, q=query, labelIds=label_ids, includeSpamTrash=True)
            .execute()
        )

        if message_ids["resultSizeEstimate"] == 0:
            logger.warning("no result data!")
            return []

        for message_id in message_ids["messages"]:
            message_detail = (
                service.users()
                .messages()
                .get(userId="me", id=message_id["id"], format = "raw")
                .execute()
            )
            '''
            message = {}
            message["id"] = message_id["id"]
            # accept only plain text
            if 'data' in message_detail['payload']['body']:
                message["body"] = decode_base64url_data(
                    message_detail["payload"]["body"]["data"]
                )

            message["subject"] = [
                header["value"]
                for header in message_detail["payload"]["headers"]
                if header["name"] == "Subject"
            ][0]

            message["from"] = [
                header["value"]
                for header in message_detail["payload"]["headers"]
                if header["name"] == "From"
            ][0]
            logger.info(message_detail["snippet"])
            messages[message_id["id"]] = message
            '''
            #print("RAW: ", message_detail["raw"])
            print(decode_base64url_data(
                message_detail["raw"]
            ))
        return messages

    except errors.HttpError as error:
        print("An error occurred: %s" % error)


def main(query="is:unread", tag='SPAM', count=3):
    creds = get_credential()
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    # get list of labels
    labels = list_labels(service, "me")
    target_label_ids = [label["id"] for label in labels if label["name"] == tag]
    messages = list_message(service, "me", query, target_label_ids, count=count)
    if messages:
        return json.dumps(messages, ensure_ascii=False, indent=4, separators=(',', ': '))
    else:
        return None


if __name__ == "__main__":
    messages_ = main(query="is:unread", tag='SPAM', count=3)
    print(messages_)
