import utils

# c is very small value which represent that a term is not included in the training set, but not 0
def classify(test_message, training_set, prior = 0.5, c = 1.0e-4):

    msg_terms = utils.get_words(test_message)

    msg_probability = 1

    for term in msg_terms:
        if term in training_set:
            msg_probability *= training_set[term]
        else:
            msg_probability *= c

    return msg_probability * prior
