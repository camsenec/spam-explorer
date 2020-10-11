"""
Send E-Mail with GMail.

Usage:
  sendmail.py <sender> <to> <subject> <message_text_file_path>  [--attach_file_path=<file_path>] [--cc=<cc>]
  sendmail.py -h | --help
  sendmail.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --attach_file_path=<file_path>     Path of file attached to message.
  --cc=<cc>     cc email address list(separated by ','). Default None.
"""
import pickle
import os.path
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
from gmail_credential import get_credential
from docopt import docopt
import logging

logger = logging.getLogger(__name__)


def create_message(sender, to, subject, message_text, cc=None):
    """
    MIMEText を base64 エンコードする
    """
    enc = "utf-8"
    message = MIMEText(message_text.encode(enc), _charset=enc)
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    if cc:
        message["Cc"] = cc
    encode_message = base64.urlsafe_b64encode(message.as_bytes())
    return {"raw": encode_message.decode()}


def create_message_with_attachment(
    sender, to, subject, message_text, file_path, cc=None
):
    """
    添付ファイルつきのMIMEText を base64 エンコードする
    """
    message = MIMEMultipart()
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    if cc:
        message["Cc"] = cc
    # attach message text
    enc = "utf-8"
    msg = MIMEText(message_text.encode(enc), _charset=enc)
    message.attach(msg)

    content_type, encoding = mimetypes.guess_type(file_path)

    if content_type is None or encoding is not None:
        content_type = "application/octet-stream"
    main_type, sub_type = content_type.split("/", 1)
    if main_type == "text":
        with open(file_path, "rb") as fp:
            msg = MIMEText(fp.read(), _subtype=sub_type)
    elif main_type == "image":
        with open(file_path, "rb") as fp:
            msg = MIMEImage(fp.read(), _subtype=sub_type)
    elif main_type == "audio":
        with open(file_path, "rb") as fp:
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
    else:
        with open(file_path, "rb") as fp:
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
    p = Path(file_path)
    msg.add_header("Content-Disposition", "attachment", filename=p.name)
    message.attach(msg)

    encode_message = base64.urlsafe_b64encode(message.as_bytes())
    return {"raw": encode_message.decode()}


def send_message(service, user_id, message):
    """
    メールを送信する

    Parameters
    ----------
    service : googleapiclient.discovery.Resource
        Gmail と通信するたえのリソース
    user_id : str
        利用者のID
    message : dict
        "raw" を key, base64 エンコーディングされた MIME Object を value とした dict

    Returns
    ----------
    なし
    """
    try:
        sent_message = (
            service.users().messages().send(userId=user_id, body=message).execute()
        )
        logger.info("Message Id: %s" % sent_message["id"])
        return None
    except errors.HttpError as error:
        logger.info("An error occurred: %s" % error)
        raise error


#  メイン処理
def main(sender, to, subject, message_text, attach_file_path, cc=None):
    # アクセストークンの取得とサービスの構築
    creds = get_credential()
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    if attach_file_path:
        # メール本文の作成
        message = create_message_with_attachment(
            sender, to, subject, message_text, attach_file_path, cc=cc
        )
    else:
        message = create_message(
            sender, to, subject, message_text, cc=cc
        )
    # メール送信
    send_message(service, "me", message)


# プログラム実行部分
if __name__ == "__main__":
    arguments = docopt(__doc__, version="0.1")
    sender = arguments["<sender>"]
    to = arguments["<to>"]
    cc = arguments["--cc"]
    subject = arguments["<subject>"]
    message_text_file_path = arguments["<message_text_file_path>"]
    attach_file_path = arguments["--attach_file_path"]

    logging.basicConfig(level=logging.DEBUG)

    with open(message_text_file_path, "r", encoding="utf-8") as fp:
        message_text = fp.read()

    main(
        sender=sender,
        to=to,
        subject=subject,
        message_text=message_text,
        attach_file_path=attach_file_path,
        cc=cc,
    )
