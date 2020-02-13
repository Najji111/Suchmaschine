# Copyright 2020, University of Freiburg,
# Chair of Algorithms and Data Structures.
# Authors: Claudius Korzen <korzen@cs.uni-freiburg.de>.
#          Patrick Brosi <brosi@cs.uni-freiburg.de>.

import readline  # NOQA
import sys

# Word and POS tag that denote the beginning of a sentence.
begin_word = "^"
begin_tag = "BEG"

# Word and POS tag that denote the end of a sentence.
end_word = "$"
end_tag = "END"

# The POS tag that denotes an entity.
entity_pos_tag = ["NNP", "NNPS"]


class NamedEntityRecognition:
    """
    A simple Named Entity Recognition engine using the Viterbi algorithm.
    """

    def __init__(self):
        """
        Creates a new Named Entity Recognition engine.
        """
        self.transition_probabilities = None
        self.emission_probabilities = None
        self.vocabulary = None


    def pos_tag(self, sentence, eps=0.01):
        """
        Computes the sequence of POS-tags for the given sentence using the
        Viterbi algorithm, as explained in the lecture.

        Returns a list of tuples (word, POS-tag) that defines the POS-tag for
        each word in the given sentence.

        >>> ner = NamedEntityRecognition()
        >>> ner.read_transition_probs_from_file("example-transition-probs.tsv")
        >>> ner.read_emission_probs_from_file("example-emission-probs.tsv")
        >>> ner.pos_tag(["James", "Bond", "is", "an", "agent"])
        ... #doctest: +NORMALIZE_WHITESPACE
        [('James', 'NNP'), ('Bond', 'NNP'), ('is', 'VB'), ('an', 'OTHER'), \
         ('agent', 'NN')]
        >>> ner.pos_tag(["Is", "James", "Bond", "an", "agent"])
        ... #doctest: +NORMALIZE_WHITESPACE
        [('Is', 'VB'), ('James', 'NNP'), ('Bond', 'NNP'), ('an', 'OTHER'), \
         ('agent', 'NN')]
        """

        print("transition")
        print(self.transition_probabilities)
        print()
        print("emission")
        print(self.emission_probabilities)
        print()
        print("vocab")
        print(self.vocabulary)
        print()
        print("tag")
        print(self.tags)
        print()


        # shot cuts
        e_p = self.emission_probabilities
        t_p = self.transition_probabilities

        #print(taged)
        if sentence[ - 1] == 1:
            taged[0] = {}
            taged[0]['BEG'] = [e_p['BEG']['^']
            return taged 

       
        taged = pos_tag(sentence[:-1])

        print(taged)
       
        # als taged words
        for i in list(taged.keys()):
            max_i = [0]
            # all tags that can follow of tag i
            for t_i in list(tp[i].keys()):
                # remember tag with highest probability
                if max_i >= res[i] * tp[i][t_i]:
                    max_i =  

        #for i in range(taged, 0, - 1):

        


        return []

    def find_named_entities(self, tagging):
        """
        Recognizes entities in the given tagging.

        Returns a list of tuples (phrase, POS-tag, is_entity), where phrase is
        a sequence of words, POS-tag is the tag for the phrase and is_entity is
        a boolean that indicates whether the phrase denotes an entity or not.

        >>> ner = NamedEntityRecognition()
        >>> ner.read_transition_probs_from_file("example-transition-probs.tsv")
        >>> ner.read_emission_probs_from_file("example-emission-probs.tsv")
        >>> tagging = ner.pos_tag(["James", "Bond", "is", "an", "agent"])
        >>> ner.find_named_entities(tagging)
        ... #doctest: +NORMALIZE_WHITESPACE
        [('James Bond', 'NNP', True), ('is', 'VB', False), \
         ('an', 'OTHER', False), ('agent', 'NN', False)]
        >>> tagging = ner.pos_tag(["James", "Bond", "is", "an", "agent", "and",
        ...    "likes", "martini"])
        >>> ner.find_named_entities(tagging)
        ... #doctest: +NORMALIZE_WHITESPACE
        [('James Bond', 'NNP', True), ('is', 'VB', False), \
         ('an', 'OTHER', False), ('agent', 'NN', False), \
         ('and', 'CC', False), ('likes', 'VB', False), \
         ('martini', 'NNP', True)]
        """

        # TODO: add your code

        return []

    def read_transition_probs_from_file(self, filename):
        """
        Reads the transition probabilities from the given file.

        The expected format of the file is one transition probability per line,
        in the format "POS-tag<TAB>POS-tag<TAB>probability"

        >>> ner = NamedEntityRecognition()
        >>> ner.read_transition_probs_from_file("example-transition-probs.tsv")
        >>> ner.transition_probabilities == {
        ...   "NNP": {"END": 0.2, "OTHER": 0.2, "NNP": 0.5, "VB": 0.3},
        ...   "BEG":   { "NNP": 0.2, "NN": 0.2, "VB": 0.4, "OTHER": 0.2 },
        ...   "NN":    { "NN": 0.3, "VB": 0.3, "END": 0.2, "CC": 0.2 },
        ...   "VB":    { "NNP": 0.4, "NN": 0.4, "OTHER": 0.2 },
        ...   "OTHER": { "NNP": 0.1, "NN": 0.5, "OTHER": 0.4 },
        ...   "CC": { "VB": 1.0 }
        ... }
        True
        """
        transition_probabilities = {}
        with open(filename) as f:
            for line in f:
                tag1, tag2, prob = line.strip().split("\t")

                if tag1 not in transition_probabilities:
                    transition_probabilities[tag1] = {}
                transition_probabilities[tag1][tag2] = float(prob)

        self.transition_probabilities = transition_probabilities

    def read_emission_probs_from_file(self, filename):
        """
        Reads the emission probabiliteis from the given file.

        The expected format of the file is one word per line, in the format
        "word<TAB>POS-tag<TAB>probability".

        >>> ner = NamedEntityRecognition()
        >>> ner.read_emission_probs_from_file("example-emission-probs.tsv")
        >>> ner.emission_probabilities == \
        { \
          "BEG":   { "^": 1 }, \
          "NNP":   { "James": 0.33, "Bond": 0.33, "martini": 0.33 }, \
          "NN":    { "agent": 0.8, "James": 0.1, "martini": 0.1 }, \
          "VB":    { "is": 0.6, "Bond": 0.2, "likes" : 0.2 }, \
          "OTHER": { "James": 0.2, "Bond": 0.2, "an": 0.6 }, \
          "CC":    { "and" : 1 }, \
          "END":   { "$": 1 } \
        }
        True
        >>> ner.vocabulary == {"^", "likes", "James", "Bond", "is", "an",
        ...                    "agent", "martini", "and", "$"}
        True
        >>> set(ner.tags) == {"BEG", "VB", "NNP", "OTHER", "NN", "CC", "END"}
        True
        """
        emission_probabilities = {}
        tags = set()
        vocabulary = set()

        with open(filename) as f:
            # Add the end word and end tag.
            emission_probabilities[begin_tag] = {begin_word: 1}
            tags.add(begin_tag)
            vocabulary.add(begin_word)

            # Add the words and tags from the file.
            for line in f:
                word, tag, prob = line.strip().split("\t")

                if tag not in emission_probabilities:
                    emission_probabilities[tag] = {}
                emission_probabilities[tag][word] = float(prob)
                tags.add(tag)
                vocabulary.add(word)

            # Add the end word and end tag.
            emission_probabilities[end_tag] = {end_word: 1}
            tags.add(end_tag)
            vocabulary.add(end_word)

        self.emission_probabilities = emission_probabilities
        self.vocabulary = vocabulary
        self.tags = list(tags)

    def read_entities_from_file(self, filename):
        """
        Reads the Wikidata entities from the given file.

        >>> ner = NamedEntityRecognition()
        >>> ner.read_entities_from_file("example-entities.tsv")
        >>> "United States of America" in ner.wikidata_entities
        True
        >>> "America" in ner.wikidata_entities
        True
        >>> "USA" in ner.wikidata_entities
        True
        >>> "Russia" in ner.wikidata_entities
        True
        >>> "Germany" in ner.wikidata_entities
        True
        >>> "Freiburg" in ner.wikidata_entities
        False
        """
        wikidata_entities = {}
        with open(filename, "r") as f:
            for i, line in enumerate(f):
                # Skip the first line (containing the header).
                if i == 0:
                    continue

                fields = line.strip().split("\t")

                entity = {}
                entity["name"] = name = fields[0]
                entity["score"] = int(fields[1])
                entity["description"] = fields[2]
                entity["wikipediaUrl"] = fields[3]
                entity["wikidataId"] = fields[4]

                # On entities with same name, take only the most popular one.
                if name not in wikidata_entities:
                    wikidata_entities[name] = entity

                if len(fields) > 5:
                    entity["synonyms"] = synonyms = fields[5].split(";")

                    # Index the entity also by its synonyms.
                    for synonym in synonyms:
                        if synonym not in wikidata_entities:
                            wikidata_entities[synonym] = entity

                if len(fields) > 6:
                    entity["imageUrl"] = fields[6]

        self.wikidata_entities = wikidata_entities


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 named_entity_recognition.py "
              "<transition_probabilities_file> <emission_probabilities_file> "
              "<entities_file>")
        exit(1)

    transition_probabilities_file = sys.argv[1]
    emission_probabilities_file = sys.argv[2]
    entities_file = sys.argv[3]

    ner = NamedEntityRecognition()

    # Read the files.
    ner.read_transition_probs_from_file(transition_probabilities_file)
    ner.read_emission_probs_from_file(emission_probabilities_file)
    ner.read_entities_from_file(entities_file)

    # TODO: add your code
