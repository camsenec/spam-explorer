from classifier import classifier, trainer, utils, categorizer
import sender, receiver
from os import listdir
from os.path import isfile, join
import sys
import time

# path for all the training data sets
spam_path = 'classifier/data/spam/'
spam_original_path = 'classifier/data/spam_original/'
easy_ham_path = 'classifier/data/easy_ham/'

def train():
    # 1. Data Loading and Training for constructing the learning model
    # Spam Training
    print('\nClassifier Training...')
    spam_training_set = {}
    ham_training_set = {}
    spam_training_set, file_count_spam_1 = trainer.train(spam_path, spam_training_set)
    spam_training_set, file_count_spam_2 = trainer.train(spam_original_path, spam_training_set)

    # calculating the occurrence for each term
    for term in spam_training_set.keys():
        spam_training_set[term] = float(spam_training_set[term]) / (file_count_spam_1 + file_count_spam_2)

    # Ham Training
    ham_training_set, file_count_ham = trainer.train(easy_ham_path, ham_training_set)

    # calculating the occurrence for each term
    for term in ham_training_set.keys():
        ham_training_set[term] = float(ham_training_set[term]) / file_count_ham
    print('done.\n')

    return spam_training_set, ham_training_set

def classify(message_file_path, spam_training_set, ham_training_set):
    # 0.8 and 0.2 the rate of mails between ones which are in spam traninig dataset and ham dataset, respectively

    mail_msg = utils.get_mail_from_file(message_file_path)

    spam_probability = classifier.classify(mail_msg, spam_training_set, prior=0.8)
    ham_probability = classifier.classify(mail_msg, ham_training_set, prior=0.2)

    if spam_probability > ham_probability:
        result = "SPAM"
    else:
        result = "HAM"

    return result

def send_routine(mail_sender, mail_receiver, subject, message_text_file_path, role):
    with open(message_text_file_path, "r", encoding="utf-8") as fp:
        message_text = fp.read()

    sender.main(
        sender=mail_sender,
        to=mail_receiver,
        subject=subject,
        message_text=message_text,
        role=role,
    )

def receive_routine(spam_sender, message_file_path):
    query="from:"+spam_sender
    receiver.main(
        query=query,
        message_file_path=message_file_path,
    )


if __name__=='__main__':
    #Training for Classifier
    spam_training_set, ham_training_set = train()

    args = sys.argv
    spam_sender = args[1]
    spam_receiver = args[2]
    subject = args[3]

    for communication_num in range(1,2):
        #spam_sender -> spam_receiver
        message_text_file_path = "mails/draft/message_" + str(communication_num) + ".txt"
        send_routine(spam_sender, spam_receiver, subject, message_text_file_path, "sender")
        time.sleep(5)

        #check mail from gmail box[by spam_receiver]
        message_file_path = "mails/inbox/message_" + str(communication_num) + ".txt"
        receive_routine(spam_sender, message_file_path)
        result = classify(message_file_path, spam_training_set, ham_training_set)
        print(result)

        #spam_receiver -> spam_sender
        message_text_file_path = "mails/draft/test.txt"
        send_routine(spam_receiver, spam_sender, subject, message_text_file_path, "receiver")
