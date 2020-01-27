"""
Copyright 2020, University of Freiburg.

Elmar Haussmann <haussmann@cs.uni-freiburg.de>
Claudius Korzen <korzen@cs.uni-freiburg.de>
Patrick Brosi <brosi@cs.uni-freiburg.de>
"""

import re
import sys

import numpy

from scipy.sparse import csr_matrix

numpy.set_printoptions(formatter={'float': lambda x: ("%.3f" % x)})


def generate_vocabularies(filename):
    """
    Reads the given file and generates vocabularies mapping from label/class to
    label ids and from word to word id.

    You should call this ONLY on your training data.
    """

    # Map from label/class to label id.
    class_vocabulary = dict()

    # Map from word to word id.
    word_vocabulary = dict()

    class_id = 0
    word_id = 0

    # Read the file (containing the training data).
    with open(filename, "r") as f:
        for line in f:
            label, text = line.strip().split('\t')

            if label not in class_vocabulary:
                class_vocabulary[label] = class_id
                class_id += 1

            # Remove all non-characters and non-digits from the text.
            text = re.sub("\\W+", " ", text.lower())
            # Split the text into words.
            words = text.split()

            # Add the words to the vocabulary.
            for word in words:
                if word not in word_vocabulary:
                    word_vocabulary[word] = word_id
                    word_id += 1

    return word_vocabulary, class_vocabulary


def read_labeled_data(filename, class_vocab, word_vocab):
    """
    Reads the given file and returns a sparse document-term matrix as well as a
    list of labels of each document. You need to provide a class and word
    vocabulary. Words not in the vocabulary are ignored. Documents labeled
    with classes not in the class vocabulary are also ignored.

    The returned document-term matrix X has size n x m, where n is the number
    of documents and m the number of word ids. The value at i, j denotes the
    number of times word id j is present in document i.

    The returned labels vector y has size n (one label for each document). The
    value at index j denotes the label (class id) of document j.

    >>> wv, cv = generate_vocabularies("example_train.txt")
    >>> X, y = read_labeled_data("example_train.txt", cv, wv)
    >>> X.todense()  # the term document matrix
    matrix([[2.000, 1.000],
            [5.000, 2.000],
            [3.000, 5.000],
            [3.000, 2.000],
            [1.000, 3.000],
            [2.000, 4.000],
            [1.000, 3.000]])
    >>> y  # the array of labels
    array([0, 0, 1, 0, 1, 1, 1])
    """

    labels = []
    row, col, value = [], [], []
    num_examples = 0
    num_cols = len(word_vocab)

    with open(filename, "r") as f:
        for i, line in enumerate(f):
            label, text = line.strip().split('\t')

            if label in class_vocab:
                num_examples += 1
                labels.append(class_vocab[label])
                words = re.sub("\\W+", " ", text.lower()).split()
                for w in words:
                    if w in word_vocab:
                        w_id = word_vocab[w]
                        row.append(i)
                        col.append(w_id)
                        # Duplicate values at the same position i,j are summed.
                        value.append(1.0)

    x = csr_matrix((value, (row, col)), shape=(num_examples, num_cols))
    y = numpy.array(labels)
    return x, y


class NaiveBayes(object):
    """
    A simple naive bayes classifier as explained in the lecture.

    >>> numpy.set_printoptions(formatter={"float": lambda x: ("%.3f" % x)})
    """

    def __init__(self):
        """
        Creates a new naive bayes classifier supporting num_classes of classes
        and num_features of words.
        """
        # The stored probabilities of each class.
        self.p_c = None
        # The stored probabilities of each word in each class
        self.p_wc = None

    def train(self, x, y):
        """
        Trains on the sparse document-term matrix X and associated labels y.

        In the test case below, p_wc is a class-term-matrix and has a row
        for each class and a column for each term. So the value at i,j is
        the p_wc for the j-th term in the i-th class.

        p_c is an array of global probabilities for each class.

        Remember to use epsilon = 1/10 for your training, as described in the
        lecture!

        >>> wv, cv = generate_vocabularies("example_train.txt")
        >>> X, y = read_labeled_data("example_train.txt", cv, wv)
        >>> nb = NaiveBayes()
        >>> nb.train(X, y)
        >>> numpy.round(numpy.exp(nb.p_wc), 3)
        array([[0.664, 0.336],
               [0.320, 0.680]])
        >>> numpy.round(numpy.exp(nb.p_c), 3)
        array([0.429, 0.571])
        """

        T = len(y) # num of labels
        T_c = [0, 0]

        col = numpy.arange(T) # doc_id
        row = numpy.array([0] * T) # label_id
        data = numpy.array([1] * T) # if doc has label
        for i in range(T):
            if y[i] > (len(T_c) - 1):
                # increase label 
                T_c += [0] * (y[i] + 1 - len(T_c))
            T_c[y[i]] += 1 # number of docs with label at pos T_{y[i]}
            row[i] = y[i]
    
        # 1xl: l:=#lable, (1,i):=%of docs with label
        self.p_c = numpy.log(numpy.array(T_c)) - numpy.log(T) # p_c 

        #lxm matrix: l:=#lable, m:=#word, (i,j):=occ. word in doc with label
        #n_wc:=cells, n_c:=sum(rows) 
        n_wc = csr_matrix((data, (row, col)), dtype=int).dot(x)
        # lx1 matrix: l:=#label, (i,1):=sum of words in docs with label
        n_c = n_wc.sum(axis = 1)

        #lxm: l:=#labels, m:=#word, (i,j):=%of this word in label
        self.p_wc = numpy.log(n_wc.toarray() + 0.1) -  \
                    numpy.log(n_c + 0.1 * x.get_shape()[1])

    def predict(self, x):
        """
        Predicts a label for each example in the document-term matrix,
        based on the learned probabities stored in this class.

        Returns a list of predicted label ids.

        >>> wv, cv = generate_vocabularies("example_train.txt")
        >>> X, y = read_labeled_data("example_train.txt", cv, wv)
        >>> nb = NaiveBayes()
        >>> nb.train(X, y)
        >>> X_test, y_test = read_labeled_data("example_test.txt", cv, wv)
        >>> nb.predict(X_test)
        array([0, 1, 0])
        >>> nb.predict(X)
        array([0, 0, 1, 0, 1, 1, 1])
        """

        # dxl: d:=#doc, l:=#label, (i,j):=%value that doc fits to label  
        helper = x.dot(self.p_wc.transpose())

        # iterate over all %vla of all docs to find larges save col with largest
        res = numpy.array([0] * helper.shape[0])
        for i in range(helper.shape[0]):
            p_max = helper[i, 0] # keep last max
            # check %value of all labels
            for j in range(1, helper.shape[1]):
                # if %value is lager oder label to doc
                if p_max < helper[i, j]:
                   res[i] = j
        return res

    def evaluate(self, x, y):
        """
        Predicts the labels of X and computes the precisions, recalls and
        F1 scores for each class.

        >>> wv, cv = generate_vocabularies("example_train.txt")
        >>> X_train, y_train = read_labeled_data("example_train.txt", cv, wv)
        >>> X_test, y_test = read_labeled_data("example_test.txt", cv, wv)
        >>> nb = NaiveBayes()
        >>> nb.train(X_train, y_train)
        >>> precisions, recalls, f1_scores = nb.evaluate(X_test, y_test)
        >>> precisions
        {0: 0.5, 1: 1.0}
        >>> recalls
        {0: 1.0, 1: 0.5}
        >>> {x: '%.2f' % f1_scores[x] for x in f1_scores}
        {0: '0.67', 1: '0.67'}
        """

        # pred labels for test file
        pred = self.predict(x)

        # (0,i):=actual labels
        # (1,i):=labels predicted 
        # (2,i):=labels in coman
        helper = numpy.array([[0, 0], [0, 0], [0, 0]]) 
        for i in range(len(y)):
            # larger label
            c_max = 0
            if y[i] >= pred[i]:
                c_max = y[i]
            else:
                c_max = pred[i]
            
            # if appending needed
            if c_max >= helper.shape[1]:
                c_ap = c_max + 1 - helper.shape[1]
                app = [[0] * c_ap, [0] * c_ap, [0] * c_ap]
                helper = numpy.concatenate((helper, app), axis=1)

            helper[0, y[i]] += 1 # #docs with label 
            helper[1, pred[i]] += 1 # docs with label
            if y[i] == pred[i]:
               helper[2, y[i]] += 1 # labes in coman
            
        res = [{}, {}, {}]
        for i in range(helper.shape[1]):
            res[0][i] = helper[2, i] / helper[1, i] # precision 
            res[1][i] = helper[2, i] / helper[0, i] # recall 
            res[2][i] = (2 * res[0][i] * res[1][i]) / \
                        (res[0][i] + res[1][i]) # F-measure 

        return res[0], res[1], res[2] 


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 naive_bayes.py <train-input> <test-input>")
        exit(1)

    train_input = sys.argv[1]
    test_input = sys.argv[2]

    word_vocab, class_vocab = generate_vocabularies(train_input)
    X_train, y_train = read_labeled_data(train_input, class_vocab, word_vocab)
    X_test, y_test = read_labeled_data(test_input, class_vocab, word_vocab)

    # Train on the training dataset.
    nb = NaiveBayes()
    nb.train(X_train, y_train)
    res = nb.predict(X_test)
    eva_p, eva_r, eva_f = nb.evaluate(X_test, y_test)  

    # Output the precision, recall, and F1 score on the test data, for
    #       each class separately as well as the (unweighted) average over all
    #       classes.
    print("class\tprecision\trecalled\tF1-score\taverage")
    #print(class_vocab[class_vocab.keys()[i]])
    for i in range(len(nb.p_c)):
        print(list(class_vocab.keys())[i] + "\t" + str(eva_p[i]) + "\t" +
        str(eva_r[i]) + "\t" + str(eva_f[i]) + "\t" + str(nb.p_c[i]))


    # TODO: Print the 30 words with the highest p_wc values per class which do
    #       not appear in the stopwords.txt provided on the Wiki.
