from classifier import utils
from monkeylearn import MonkeyLearn

def extract_scammer_name(message):
    ml = MonkeyLearn('d31c9827434f85201fc8ba34de9fa26a2ff91936')
    data = [message]
    model_id = 'ex_SmwSdZ3C'
    result = ml.extractors.extract(model_id, data)
    scammer_name = result.body[0]["extractions"][0]["parsed_value"]
    return scammer_name

def reply(inserted, reply_number):
    text = ""
    if reply_number == 1:
        text += "Hi! %(scammer_name)s\n" % inserted
        text += "Thank you for contacting me.\n"
        text += "My name is %(myname)s.\n" % inserted
        text += "Please tell me more detailed infromation\n"
        text += "Sincerely Yours,\n\n"
        text += "--------------------------------------------------\n"
        text += "%(myname)s\n\n" % inserted

    elif reply_number == 2:
        text += "Hi! %(scammer_name)s\n" % inserted
        text += "Thank you for contacting me.\n"
        #text += "My name is %(myname)s.\n" % inserted
        text += "I'll follow your instruction\n"
        text += "Sincerely Yours,\n\n"
        text += "--------------------------------------------------\n"
        text += "%(myname)s\n\n" % inserted

    elif reply_number == 3:
        text += "Hi! %(scammer_name)s\n" % inserted
        text += "Thank you for contacting me.\n"
        #text += "My name is %(myname)s.\n" % inserted
        text += "I cannot tell you my personal information\n"
        text += "Sincerely Yours,\n\n"
        text += "--------------------------------------------------\n"
        text += "%(myname)s\n\n" % inserted

    else:
        pass

    return text


def generate_mail(message, category_tag_list, reply_number):
    if category_tag_list["reply"] == True:
        inserted = {}
        scammer_name = extract_scammer_name(message)
        inserted["scammer_name"] = scammer_name
        inserted["myname"] = "Morris Briggs"
        reply_text = reply(inserted, reply_number)
    elif category_tag_list["chat"] == True or category_tag_list["hyperlink"] == True or category_tag_list["money"] == True:
        pass
    else:
        pass
    return reply_text

if __name__ == '__main__':
    message = "Complements of the day,\nI am Bowman, I am Professional Lawyer, I have something important Urgently to discuss with you concerning your late Japanese family,\nWaiting for your respond to proceed,\n\nBowman,"
    category_tag_list = {"chat": False, "reply": True, "hyperlink":False, "money": False}
    reply_number = 1
    generate_mail(message, category_tag_list, reply_number)
