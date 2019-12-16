"""
Copyright 2019, University of Freiburg
Chair of Algorithms and Data Structures.
Hannah Bast <bast@cs.uni-freiburg.de>
Claudius Korzen <korzen@cs.uni-freiburg.de>
Patrick Brosi <brosi@cs.uni-freiburg.de>
"""

import math
import re
import readline  # NOQA
import sys


DEFAULT_B = 0.75
DEFAULT_K = 1.75


class InvertedIndex:
    """
    A simple inverted index that uses BM25 scores.
    """

    def __init__(self):
        """
        Creates an empty inverted index.
        """
        self.inverted_lists = {}  # The inverted lists.
        self.docs = []  # The docs, each in form (title, description).
        self.doc_lengths = []  # The document lengths (= number of words).

    def build_from_file(self, file_name, b=None, k=None):
        """
        Construct the inverted index from the given file. The expected format
        of the file is one document per line, in the format
        <title>TAB<description>. Each entry in the inverted list associated to
        a word should contain a document id and a BM25 score. Compute the BM25
        scores as follows:

        (1) In a first pass, compute the inverted lists with tf scores (that
            is the number of occurrences of the word within the <title> and the
            <description> of a document). Further, compute the document length
            (DL) for each document (that is the number of words in the <title>
            and the <description> of a document). Afterwards, compute the
            average document length (AVDL).
        (2) In a second pass, iterate each inverted list and replace the tf
            scores by BM25 scores, defined as:
            BM25 = tf * (k+1) / (k * (1 - b + b * DL/AVDL) + tf) * log2(N/df),
            where N is the total number of documents and df is the number of
            documents that contains the word.

        On reading the file, use UTF-8 as the standard encoding. To split the
        texts into words, use the method introduced in the lecture. Make sure
        that you ignore empty words.

        >>> ii = InvertedIndex()
        >>> ii.build_from_file("example.txt", b=0, k=float("inf"))
        >>> inv_lists = sorted(ii.inverted_lists.items())
        >>> [(w, [(i, '%.3f' % tf) for i, tf in l]) for w, l in inv_lists]
        ... # doctest: +NORMALIZE_WHITESPACE
        [('animated', [(1, '0.415'), (2, '0.415'), (4, '0.415')]),
         ('animation', [(3, '2.000')]),
         ('film', [(2, '1.000'), (4, '1.000')]),
         ('movie', [(1, '0.000'), (2, '0.000'), (3, '0.000'), (4, '0.000')]),
         ('non', [(2, '2.000')]),
         ('short', [(3, '1.000'), (4, '2.000')])]

        >>> ii = InvertedIndex()
        >>> ii.build_from_file("example.txt", b=0.75, k=1.75)
        >>> inv_lists = sorted(ii.inverted_lists.items())
        >>> [(w, [(i, '%.3f' % tf) for i, tf in l]) for w, l in inv_lists]
        ... # doctest: +NORMALIZE_WHITESPACE
        [('animated', [(1, '0.459'), (2, '0.402'), (4, '0.358')]),
         ('animation', [(3, '2.211')]),
         ('film', [(2, '0.969'), (4, '0.863')]),
         ('movie', [(1, '0.000'), (2, '0.000'), (3, '0.000'), (4, '0.000')]),
         ('non', [(2, '1.938')]),
         ('short', [(3, '1.106'), (4, '1.313')])]
        """

        b = DEFAULT_B if b is None else b
        k = DEFAULT_K if k is None else k

        # First pass: Compute (1) the inverted lists with tf scores and (2) the
        # document lengths.
        with open(file_name, "r", encoding="utf-8") as f:
            doc_id = 0
            for line in f:
                line = line.strip()

                dl = 0  # Compute the document length (number of words).
                doc_id += 1

                for word in re.split("[^A-Za-z]+", line):
                    word = word.lower().strip()

                    # Ignore the word if it is empty.
                    if len(word) == 0:
                        continue

                    dl += 1

                    if word not in self.inverted_lists:
                        # The word is seen for first time, create new list.
                        self.inverted_lists[word] = [(doc_id, 1)]
                        continue

                    # Get last posting to check if the doc was already seen.
                    last = self.inverted_lists[word][-1]
                    if last[0] == doc_id:
                        # The doc was already seen, increment tf by 1.
                        self.inverted_lists[word][-1] = (doc_id, last[1] + 1)
                    else:
                        # The doc was not already seen, set tf to 1.
                        self.inverted_lists[word].append((doc_id, 1))

                # Store the doc as a tuple (title, description).
                self.docs.append(tuple(line.split("\t")))

                # Register the document length.
                self.doc_lengths.append(dl)

        # Compute N (the total number of documents).
        n = len(self.docs)
        # Compute AVDL (the average document length).
        avdl = sum(self.doc_lengths) / n

        # Second pass: Iterate the inverted lists and replace the tf scores by
        # BM25 scores, defined as follows:
        # BM25 = tf * (k + 1) / (k * (1 - b + b * DL / AVDL) + tf) * log2(N/df)
        for word, inverted_list in self.inverted_lists.items():
            for i, (doc_id, tf) in enumerate(inverted_list):
                # Obtain the document length (dl) of the document.
                dl = self.doc_lengths[doc_id - 1]  # doc_id is 1-based.
                # Compute alpha = (1 - b + b * DL / AVDL).
                alpha = 1 - b + (b * dl / avdl)
                # Compute tf2 = tf * (k + 1) / (k * alpha + tf).
                tf2 = tf * (1 + (1 / k)) / (alpha + (tf / k)) if k > 0 else 1
                # Compute df (that is the length of the inverted list).
                df = len(self.inverted_lists[word])
                # Compute the BM25 score = tf' * log2(N/df).
                inverted_list[i] = (doc_id, tf2 * math.log(n / df, 2))

    def merge(self, list1, list2):
        """
        Compute the union of the two given inverted lists in linear time
        (linear in the total number of entries in the two lists), where the
        entries in the inverted lists are postings of form (doc_id, bm25_score)
        and are expected to be sorted by doc_id, in ascending order.

        >>> ii = InvertedIndex()
        >>> l1 = ii.merge([(1, 2.1), (5, 3.2)], [(1, 1.7), (2, 1.3), (6, 3.3)])
        >>> [(id, "%.1f" % tf) for id, tf in l1]
        [(1, '3.8'), (2, '1.3'), (5, '3.2'), (6, '3.3')]

        >>> l2 = ii.merge([(3, 1.7), (5, 3.2), (7, 4.1)], [(1, 2.3), (5, 1.3)])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        [(1, '2.3'), (3, '1.7'), (5, '4.5'), (7, '4.1')]

        >>> l2 = ii.merge([], [(1, 2.3), (5, 1.3)])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        [(1, '2.3'), (5, '1.3')]

        >>> l2 = ii.merge([(1, 2.3)], [])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        [(1, '2.3')]

        >>> l2 = ii.merge([], [])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        []
        """
        i = 0  # The pointer in the first list.
        j = 0  # The pointer in the second list.
        result = []

        # Iterate the lists in an interleaving order and aggregate the scores.
        while i < len(list1) and j < len(list2):
            if i < list1[i][0] == list2[j][0]:
                result.append((list1[i][0], list1[i][1] + list2[j][1]))
                i += 1
                j += 1
            elif list1[i][0] < list2[j][0]:
                result.append(list1[i])
                i += 1
            else:
                result.append(list2[j])
                j += 1

        # Append the rest of the first list.
        while i < len(list1):
            result.append(list1[i])
            i += 1

        # Append the rest of the second list.
        while j < len(list2):
            result.append(list2[j])
            j += 1

        return result

    def process_query(self, keywords, use_refinements=False):
        """
        Process the given keyword query as follows: Fetch the inverted list for
        each of the keywords in the query and compute the union of all lists.
        Sort the resulting list by BM25 scores in descending order.

        This method returns _all_ results for the given query, not just the
        top 3!

        If you want to implement some ranking refinements, make these
        refinements optional (their use should be controllable via the
        use_refinements flag).

        >>> ii = InvertedIndex()
        >>> ii.inverted_lists = {
        ... "foo": [(1, 0.2), (3, 0.6)],
        ... "bar": [(1, 0.4), (2, 0.7), (3, 0.5)],
        ... "baz": [(2, 0.1)]}
        >>> result = ii.process_query(["foo", "bar"], use_refinements=False)
        >>> [(id, "%.1f" % tf) for id, tf in result]
        [(3, '1.1'), (2, '0.7'), (1, '0.6')]
        """
        if not keywords:
            return []

        # Fetch the inverted lists for each of the given keywords.
        lists = []
        for keyword in keywords:
            if keyword in self.inverted_lists:
                lists.append(self.inverted_lists[keyword])

        # Compute the union of all inverted lists.
        if len(lists) == 0:
            return []

        union = lists[0]
        for i in range(1, len(lists)):
            union = self.merge(union, lists[i])

        # Filter all postings with BM25 = 0.
        union = [x for x in union if x[1] != 0]

        # Sort the postings by BM25 scores, in descending order.
        return sorted(union, key=lambda x: x[1], reverse=True)

    def render_output(self, postings, keywords, k=3):
        """
        Render the output for the top-k of the given postings. Fetch the
        the titles and descriptions of the related docs and highlight the
        occurences of the given keywords in the output, using ANSI escape
        codes.
        """

        # Compile a pattern to identify the given keywords in a string.
        p = re.compile('\\b(' + '|'.join(keywords) + ')\\b', re.IGNORECASE)

        # Output at most k matching docs.
        for i in range(min(len(postings), k)):
            doc_id, tf = postings[i]
            title, desc = self.docs[doc_id - 1]  # doc_id is 1-based.

            # Highlight the keywords in the title in bold and red.
            title = re.sub(p, "\033[0m\033[1;31m\\1\033[0m\033[1m", title)

            # Print the rest of the title in bold.
            title = "\033[1m%s\033[0m" % title

            # Highlight the keywords in the description in red.
            desc = re.sub(p, "\033[31m\\1\033[0m", desc)

            print("\n%s\n%s" % (title, desc))

        print("\n# total hits: %s." % len(postings))


if __name__ == "__main__":
    # Parse the command line arguments.
    if len(sys.argv) < 2:
        print("Usage: python3 inverted_index.py <file> [<b>] [<k>]")
        sys.exit()

    file_name = sys.argv[1]
    b = float(sys.argv[2]) if len(sys.argv) > 2 else None
    k = float(sys.argv[3]) if len(sys.argv) > 3 else None

    # Create a new inverted index from the given file.
    print("Reading from file '%s'." % file_name)
    ii = InvertedIndex()
    ii.build_from_file(file_name, b=b, k=k)

    while True:
        # Ask the user for a keyword query.
        query = input("\nYour keyword query: ")

        # Split the query into keywords.
        keywords = [x.lower().strip() for x in re.split("[^A-Za-z]+", query)]

        # Process the keywords.
        postings = ii.process_query(keywords)

        # Render the output (with ANSI codes to highlight the keywords).
        ii.render_output(postings, keywords)
