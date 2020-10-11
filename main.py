from classifier import classifier, trainer, utils, categorizer
import sender, receiver
from os import listdir
from os.path import isfile, join
import sys

# path for all the training data sets
spam_path = 'categorizer/classifier/data/spam/'
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

    mail_msg = utils.get_mail_from_file(mail_path + mail_name)

    return spam_training_set, ham_training_set

def classify(spam_training_set, ham_training_set):
    # 0.8 and 0.2 the rate of mails between ones which are in spam traninig dataset and ham dataset, respectively
    spam_probability = classifier.classify(mail_msg, spam_training_set, prior=0.8)
    ham_probability = classifier.classify(mail_msg, ham_training_set, prior=0.2)

    if spam_probability > ham_probability:
        result = "SPAM"
        spam_classified_mails.append(mail_path + mail_name)
    else:
        result = "HAM"

    return result

def send_routine(spam_sender, spam_receiver, subject, message_text_file_path, ):
    with open(message_text_file_path, "r", encoding="utf-8") as fp:
        message_text = fp.read()

    sender.main(
        sender=spam_sender,
        to=spam_receiver,
        subject=subject,
        message_text=message_text,
    )

def receive_routine(spam_sender):
    query="from:"+spam_sender
    messages_ = receiver.main(query=query, tag='SPAM', count=1)
    print(messages_)


if __name__=='__main__':
    #Training for Classifier
    spam_training_set, ham_training_set = train()

    args = sys.argv
    spam_sender = args[1]
    spam_receiver = args[2]
    subject = args[3]
    message_text_file_path = "mails/message_1.txt"

    for communication_num in range(1,2):
        send_routine(spam_sender, spam_receiver, subject, message_text_file_path)


    result = classify(spam_training_set, ham_training_set)
    flags = categorizer.categorize_action(mail_msg)
