# for tokenize
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize

# add path to NLTK file
nltk.data.path = ['classifier/nltk_data']
# load stopwords
stopwords = set(stopwords.words('english'))

def get_words(message):

    all_words = set(wordpunct_tokenize(message.replace('=\\n', '').lower()))
    msg_words = [word for word in all_words if word not in stopwords and len(word) > 2]

    return msg_words

def get_mail_from_file(file_name):

    message = ''

    with open(file_name, 'r', encoding='ISO-8859-1') as mail_file:

        for line in mail_file:
            # the contents of the actual mail start after the first newline
            # so find it, and then extract the words
            if line == '\n':
                # make a string out of the remaining lines
                for line in mail_file:
                    message += line

    return message
