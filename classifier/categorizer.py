from classifier import utils

category_action = ["chat", "hyperlink", "money", "reply"]

def judge(term):
    if term == "talk" or term == "chat" or term == "LINE":
        return category_action[0]
    elif term == "link" or term == "http" or term == "https":
        return category_action[1]
    elif term == "money" or term == "coin":
        return category_action[2]
    elif term == "reply" or term == "respond":
        return category_action[3]
    else:
        return None

def categorize(spam_file_path):
    message = utils.get_mail_from_file(spam_file_path)
    msg_terms = utils.get_words(message)
    flags = dict()

    for category in category_action:
        flags[category] = False

    for term in msg_terms:
        flags[judge(term)] = True

    return flags
