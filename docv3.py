"""
docv3.py -- document and query parsing for IFQ647 Assignment 1 (Question 1).

Contents
    DocV3            bag-of-words representation of one news document
    load_stop_words  read the stop-word file into a list
    tokenize         turn one line of raw text into a list of words
    make_term        turn one word into an index term (or None)
    Parse_Docs       Task 1.1 -- parse a folder of XML files
    Parse_Q          Task 1.2 -- parse a query string
    read_titles      helper used by Question 2 to get <title> queries

DEFINITIONS (required by Task 1.1)
    WORD  A word is a maximal run of English letters (a-z, A-Z) found in the
          text after (1) XML tags are removed, (2) digits are deleted and
          (3) every punctuation character is replaced by a space.
          So "fuel-efficient" is two words (fuel, efficient), "car's" is two
          words (car, s), "16-point" is one word (point) and "1997" is not a
          word at all.  Every word counts towards the document length
          (doc_size), including stop words.

    TERM  A term is the index form of a word: the word is lower-cased and
          stemmed with the Porter2 algorithm, and it is kept only if the stem
          (a) has more than two characters and (b) is not in the stop-word
          list.  Terms are the keys of DocV3.terms, e.g. the words "Ranks"
          and "ranking" both become the term "rank".

    Note: XML character entities are not decoded, so &quot; contributes the
    word "quot".  This matches the sample output in the specification.

Only the standard library and the stemming package supplied with the
assignment data are used.  The XML files are read as plain text, line by
line, so no XML library is needed.
"""
import os
import string

from stemming.porter2 import stem

# Translation tables used by tokenize(); built once because they never change.
_REMOVE_DIGITS = str.maketrans("", "", string.digits)
_PUNCT_TO_SPACE = str.maketrans(string.punctuation, " " * len(string.punctuation))

MIN_TERM_LENGTH = 3   # terms shorter than this (e.g. "s", "us") are discarded


class DocV3:
    """Bag-of-words representation of one RCV1v3 news document."""

    def __init__(self, newsID):
        self.newsID = newsID    # value of 'itemid' in <newsitem ...>
        self.terms = {}         # {term (str): frequency (int)}
        self.doc_size = 0       # document length = total number of words

    def add_term(self, term):
        """Add a new term with frequency 1, or add 1 to an existing term."""
        self.terms[term] = self.terms.get(term, 0) + 1

    def getNewsID(self):
        """Return the document ID."""
        return self.newsID

    def get_termList(self):
        """Return a sorted (alphabetical) list of all terms in the document."""
        return sorted(self.terms)

    def get_sorted_terms(self):
        """Return [(term, freq), ...] sorted by frequency, highest first.

        Terms with the same frequency keep the order in which they first
        appeared in the document (Python's sort is stable).
        """
        return sorted(self.terms.items(), key=lambda item: item[1], reverse=True)

    # Accessor and mutator for doc_size (required by Task 3.1).
    def get_doc_size(self):
        """Accessor: return the document length (number of words)."""
        return self.doc_size

    def set_doc_size(self, doc_size):
        """Mutator: store the document length (number of words)."""
        self.doc_size = doc_size


def load_stop_words(stopwords_file):
    """Read the comma-separated stop-word file and return it as a list.

    The supplied 'common-english-words.txt' is used unchanged.
    """
    with open(stopwords_file, "r", encoding="utf-8") as file:
        stopwordList = file.read().strip().split(",")
    return stopwordList


def tokenize(text):
    """Split raw text into words, following the WORD definition above.

    Used for both documents and queries so that they are tokenized in exactly
    the same way.
    """
    text = text.translate(_REMOVE_DIGITS).translate(_PUNCT_TO_SPACE)
    return text.split()


def make_term(word, stop_words):
    """Turn a word into a term, following the TERM definition above.

    Returns the stemmed term, or None if the word must be ignored (too short
    or a stop word).
    """
    term = stem(word.lower())
    if len(term) < MIN_TERM_LENGTH or term in stop_words:
        return None
    return term


def _parse_file(path, stop_words):
    """Parse one XML file and return it as a DocV3 object."""
    doc = DocV3(None)
    word_count = 0
    in_text = False                       # True while inside <text>...</text>
    with open(path, "r", encoding="iso-8859-1") as file:
        for line in file:
            line = line.strip()
            if not in_text:
                if line.startswith("<newsitem "):
                    # e.g. <newsitem itemid="741299" id="root" ...>
                    doc.newsID = line.split('itemid="')[1].split('"')[0]
                elif line.startswith("<text>"):
                    in_text = True
            elif line.startswith("</text>"):
                break
            else:
                line = line.replace("<p>", "").replace("</p>", "")   # drop tags
                for word in tokenize(line):
                    word_count += 1
                    term = make_term(word, stop_words)
                    if term is not None:
                        doc.add_term(term)
    doc.set_doc_size(word_count)
    return doc


def Parse_Docs(stop_words, inputfolder):
    """Task 1.1 -- parse every XML file in inputfolder.

    stop_words  -- list of stop words
    inputfolder -- folder that holds the XML files (e.g. data/RCV1v3)
    Returns a dictionary {newsID: DocV3 object}.
    """
    stop_set = set(stop_words)            # set gives fast membership tests
    coll = {}
    for file_name in sorted(os.listdir(inputfolder)):
        if file_name.endswith(".xml"):
            doc = _parse_file(os.path.join(inputfolder, file_name), stop_set)
            coll[doc.getNewsID()] = doc
    return coll


def Parse_Q(query, stop_words):
    """Task 1.2 -- parse a query string into a {term: frequency} dictionary.

    Uses the same tokenize() and make_term() steps as Parse_Docs().
    """
    stop_set = set(stop_words)
    query_terms = {}
    for word in tokenize(query):
        term = make_term(word, stop_set)
        if term is not None:
            query_terms[term] = query_terms.get(term, 0) + 1
    return query_terms


def read_titles(inputfolder):
    """Return {newsID: title text} for every XML file in inputfolder.

    Extra helper (not in the specification): Question 2 uses document titles
    as its test queries, so the <title>...</title> line is read here.
    """
    titles = {}
    for file_name in sorted(os.listdir(inputfolder)):
        if not file_name.endswith(".xml"):
            continue
        news_id = None
        with open(os.path.join(inputfolder, file_name), "r",
                  encoding="iso-8859-1") as file:
            for line in file:
                line = line.strip()
                if line.startswith("<newsitem "):
                    news_id = line.split('itemid="')[1].split('"')[0]
                elif line.startswith("<title>"):
                    titles[news_id] = (line.replace("<title>", "")
                                       .replace("</title>", ""))
                    break
    return titles
