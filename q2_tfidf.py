"""
q2_tfidf.py -- Question 2: TF*IDF term weighting and a TF*IDF-based IR model.

Contents
    df           Task 2.1 -- document frequency of every term
    tfidf        Task 2.2 -- TF*IDF weights of one document, Eq. (1)
    rank_tfidf   abstract ranking model, Eq. (2)
    cosine       cosine similarity (only used for the comparison/observation)
    main         Task 2.3 -- top-25 terms per document, then rankings

Run this file directly.  It prints the results and saves the same text to
'outputs/<your full name>_Q2.txt'.
"""
import math

import config
from docv3 import Parse_Docs, Parse_Q, load_stop_words, read_titles

TOP_TERMS = 25                                   # terms printed per document
TITLE_DOC_IDS = ["86961", "741299", "809481"]    # titles used as test queries
EXTRA_QUERIES = ["US EPA ranks Geo Metro car most fuel-efficient 1997 car."]


def df(coll):
    """Task 2.1 -- return {term: df}, where df is the number of documents in
    the collection coll ({newsID: DocV3}) that contain the term."""
    d_f = {}
    for doc in coll.values():
        for term in doc.terms:               # each term counted once per doc
            d_f[term] = d_f.get(term, 0) + 1
    return d_f


def tfidf(doc, d_f, ndocs):
    """Task 2.2 -- return {term: tfidf_weight} for one document, using Eq. (1):

        d_ik = (log(f_ik) + 1) * log(N / n_k)
               ---------------------------------------------------
               sqrt( sum_x [ (log(f_ix) + 1) * log(N / n_x) ]^2 )

    doc   -- a DocV3 object or a {term: freq} dictionary
    d_f   -- {term: df} dictionary
    ndocs -- N, the number of documents in the collection
    log is the natural logarithm.
    """
    terms = doc.terms if hasattr(doc, "terms") else doc
    weights = {}
    for term, freq in terms.items():
        weights[term] = (math.log(freq) + 1) * math.log(ndocs / d_f[term])
    # Normalise by the vector length so that long documents are not favoured.
    length = math.sqrt(sum(weight ** 2 for weight in weights.values()))
    if length > 0:
        for term in weights:
            weights[term] = weights[term] / length
    return weights


def rank_tfidf(query_terms, doc_weights):
    """Abstract ranking model, Eq. (2): R(Q, D) = sum_i g_i(Q) * f_i(D).

    g_i(Q) -- frequency of term i in the parsed query
    f_i(D) -- TF*IDF weight of term i in document D (0 if D lacks the term)
    query_terms -- {term: freq} from Parse_Q()
    doc_weights -- {newsID: {term: tfidf_weight}}
    Returns {newsID: score}.
    """
    scores = {}
    for newsID, weights in doc_weights.items():
        scores[newsID] = sum(q_freq * weights.get(term, 0)
                             for term, q_freq in query_terms.items())
    return scores


def cosine(query_terms, weights):
    """Cosine similarity between the query vector and one document vector.

    Extra function, used only to compare with the abstract ranking model.
    """
    dot = sum(q_freq * weights.get(term, 0) for term, q_freq in query_terms.items())
    q_len = math.sqrt(sum(q_freq ** 2 for q_freq in query_terms.values()))
    d_len = math.sqrt(sum(weight ** 2 for weight in weights.values()))
    if q_len == 0 or d_len == 0:
        return 0
    return dot / (q_len * d_len)


def sort_scores(scores):
    """Return [(newsID, score), ...] sorted by score, highest first."""
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def main():
    stopwordList = load_stop_words(config.STOPWORDS_FILE)
    coll = Parse_Docs(stopwordList, config.INPUT_FOLDER)
    ndocs = len(coll)
    d_f = df(coll)

    lines = ["IFQ647 Assignment 1 - Question 2 - {} ({})".format(
        config.STUDENT_NAME, config.STUDENT_ID), ""]

    # Task 2.1 output: document frequencies, highest first.
    lines.append("There are {} documents in this data set and contains {} "
                 "terms".format(ndocs, len(d_f)))
    lines.append("The following are the terms' document-frequency:")
    for term, freq in sort_scores(d_f):
        lines.append("{} : {}".format(term, freq))
    lines.append("")

    # Task 2.3 output, part 1: top-25 TF*IDF terms of every document.
    doc_weights = {}
    for newsID, doc in coll.items():
        doc_weights[newsID] = tfidf(doc, d_f, ndocs)
        lines.append("Document {} contains {} terms".format(newsID, len(doc.terms)))
        for term, weight in sort_scores(doc_weights[newsID])[:TOP_TERMS]:
            lines.append("{} : {}".format(term, weight))
        lines.append("")

    # Task 2.3 output, part 2: TF*IDF-based IR model on title queries.
    titles = read_titles(config.INPUT_FOLDER)
    queries = [titles[newsID] for newsID in TITLE_DOC_IDS] + EXTRA_QUERIES
    for query in queries:
        query_terms = Parse_Q(query, stopwordList)
        ranking = sort_scores(rank_tfidf(query_terms, doc_weights))
        lines.append("The Ranking Result for query: {}".format(query))
        for newsID, score in ranking:
            lines.append("{} : {}".format(newsID, score))
        lines.append("")

        # Comparison with cosine similarity (for the required observation).
        cos_scores = {newsID: cosine(query_terms, doc_weights[newsID])
                      for newsID in doc_weights}
        cos_ranking = sort_scores(cos_scores)
        same = [n for n, _ in ranking] == [n for n, _ in cos_ranking]
        lines.append("Cosine similarity ranking for the same query:")
        for newsID, score in cos_ranking:
            lines.append("{} : {}".format(newsID, score))
        lines.append("Same document order as the abstract model: {}".format(same))
        lines.append("")

    # Observation required by Task 2.3.
    magnitudes = [math.sqrt(sum(w ** 2 for w in weights.values()))
                  for weights in doc_weights.values()]
    lines.append("Observation on cosine similarity:")
    lines.append("The magnitude of every document vector lies between {} and {}."
                 .format(min(magnitudes), max(magnitudes)))
    lines.append("Eq. (1) already divides each weight by the document vector's "
                 "length, so every document vector has magnitude 1. Cosine "
                 "similarity is therefore the abstract score divided by the "
                 "query vector's length, which is the same for every document. "
                 "The scores are smaller, but the ranking order is identical.")

    output = "\n".join(lines)
    print(output)
    with open(config.output_path("Q2"), "w", encoding="utf-8") as file:
        file.write(output)


if __name__ == "__main__":
    main()
