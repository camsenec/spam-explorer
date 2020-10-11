import classifier
import trainer
import utils
import categorizer

# for reading all the files
from os import listdir
from os.path import isfile, join

# path for all the training data sets
spam_path = 'data/spam/'
spam_original_path = 'data/spam_original/'
easy_ham_path = 'data/easy_ham/'

# path for test dataset
spam2_path = 'data/spam_2/'
easy_ham2_path = 'data/easy_ham_2/'
hard_ham_path = 'data/hard_ham_2/'
spam_original2_path = 'data/spam_original_2/'

test_paths = [spam2_path, easy_ham2_path, hard_ham_path, spam_original2_path]

if __name__=="__main__":

    #0. File Open
    try:
        with open("result.txt", mode='x') as f:
            f.write("")
    except FileExistsError:
        with open("result.txt", mode='w') as f:
            f.write("")

    # 1. Data Loading and Training for constructing the learning model
    # Spam Training
    print('\nTraining...')
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

    # 2. Test the prediction accuracy
    for mail_path in test_paths:

        mails_in_dir = [mail_file for mail_file in listdir(mail_path) if isfile(join(mail_path, mail_file))]

        results = {}
        spam_classified_mails = []
        results['spam'] = 0
        results['ham'] = 0

        print('\n\nRunning classifier on files in ', mail_path[5:-1], '...')
        with open("result.txt", mode='a') as f:
            f.write('\nRunning classifier on files in ' + mail_path[5:-1] + '...\n')


        # classify each mail in test folder
        for mail_name in mails_in_dir:

            if mail_name == 'cmds':
                continue

            mail_msg = utils.get_mail_from_file(mail_path + mail_name)

            # 0.8 and 0.2 the rate of mails between ones which are in spam traninig dataset and ham dataset, respectively
            spam_probability = classifier.classify(mail_msg, spam_training_set, prior=0.8)
            ham_probability = classifier.classify(mail_msg, ham_training_set, prior=0.2)

            if spam_probability > ham_probability:
                results['spam'] += 1
                spam_classified_mails.append(mail_path + mail_name)
            else:
                results['ham'] += 1

            total_files = results['spam'] + results['ham']
            spam_fraction = float(results['spam']) / total_files
            ham_fraction = 1 - spam_fraction

        print("Fraction of spam messages =", spam_fraction)
        print("Fraction of ham messages =\n", ham_fraction)
        with open("result.txt", mode='a') as f:
            f.write('Fraction of spam messages =' + str(spam_fraction) + '\n')
            f.write('Fraction of ham messages =' + str(ham_fraction) + '\n')

        print("========Category of Mails classified as Spam========")
        print("Expected Action: Email\tChat\tSite Access\tMoney\tReply")
        with open("result.txt", mode='a') as f:
            f.write("========Category of Mails classified as Spam========\n")
            f.write("Expected Action: Email Name, Chat, Site Access, Money, Reply\n")
            for spam_path in spam_classified_mails:
                mail_msg = utils.get_mail_from_file(spam_path)
                flags = categorizer.categorize_action(mail_msg)
                print(spam_path, "\t", flags[categorizer.category_action[0]], "\t", flags[categorizer.category_action[1]], "\t", flags[categorizer.category_action[2]], "\t", flags[categorizer.category_action[3]])
                f.write(spam_path + "\t" + str(flags[categorizer.category_action[0]]) + "\t" + str(flags[categorizer.category_action[1]]) + "\t" + str(flags[categorizer.category_action[2]]) + "\t" + str(flags[categorizer.category_action[3]]) + "\n")
