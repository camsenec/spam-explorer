from os import listdir
from os.path import isfile, join
import utils


def train(path, training_set):

    mails_in_dir = [mail_file for mail_file in listdir(path) if isfile(join(path, mail_file))]

    # count of cmds in the directory
    cmds_count = 0
    # total number of files in the directory
    total_file_count = len(mails_in_dir)

    for mail_name in mails_in_dir:

        # The given dataset includes cmd files, so we remove them.
        if mail_name == 'cmds':
            cmds_count += 1
            continue

        # get the message in the mail, eliminating stop words
        message = utils.get_mail_from_file(path + mail_name)

        # extract words from the message
        terms = utils.get_words(message)

        # count up then number of terms included in the message
        for term in terms:
            if term in training_set:
                training_set[term] = training_set[term] + 1
            else:
                training_set[term] = 1


    total_file_count -= cmds_count

    return training_set, total_file_count
