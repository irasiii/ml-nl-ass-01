"""
q3_bm25.py -- Question 3: BM25-based IR model.

Contents
    avg_length   Task 3.1 -- average document length of a collection
    my_bm25      Task 3.2 -- BM25 score of every document for a query, Eq. (3)
    main         Task 3.3 -- rank the collection for the four required queries

Run this file directly.  It prints the results and saves the same text to
'outputs/<your full name>_Q3.txt'.
"""
import math

import config
from docv3 import Parse_Docs, Parse_Q, load_stop_words
from q2_tfidf import df, sort_scores

# BM25 parameters (typical values from the lecture notes).
K1 = 1.2     # controls how quickly term frequency saturates
K2 = 100     # controls the effect of query term frequency
B = 0.75     # strength of the document length normalisation
# No relevance information is available, so R = r_i = 0.
R = 0
r_i = 0

TOP_N = 5
QUERIES = [
    "The British-Fashion Awards",
    "Rocket attacks",
    "Broadcast Fashion Awards",
    "US EPA ranks Geo Metro car most fuel-efficient 1997 car.",
]


def avg_length(coll):
    """Task 3.1 -- return the average document length of collection coll.

    Each DocV3 already stores its length (set by the doc_size mutator while
    parsing), so the lengths are summed with the accessor and averaged.
    """
    totalDocLength = 0
    for doc in coll.values():
        totalDocLength += doc.get_doc_size()
    return totalDocLength / len(coll) if coll else 0


def my_bm25(coll, q, df, stop_words=None):
    """Task 3.2 -- return {newsID: bm25_score} for every document in coll.

    Eq. (3), natural log:
        sum over query terms i of
            log( ((r_i+0.5)/(R-r_i+0.5)) / ((n_i-r_i+0.5)/(N-n_i-R+r_i+0.5)) )
            * ((k1+1)*f_i) / (K+f_i)
            * ((k2+1)*qf_i) / (k2+qf_i)
        with K = k1*((1-b) + b*dl/avdl)

    coll -- {newsID: DocV3}
    q    -- the original query string (parsed here with Parse_Q)
    df   -- {term: df} dictionary
    stop_words -- extra optional parameter: the stop-word list for Parse_Q.
                  It is loaded from the stop-word file when not given, so the
                  function can still be called as my_bm25(coll, q, df).

    A query term that does not occur in the collection has n_i = 0 and
    f_i = 0, so it adds nothing to any score.
    """
    if stop_words is None:
        stop_words = load_stop_words(config.STOPWORDS_FILE)
    query_terms = Parse_Q(q, stop_words)
    N = len(coll)
    avdl = avg_length(coll)

    scores = {}
    for newsID, doc in coll.items():
        K = K1 * ((1 - B) + B * doc.get_doc_size() / avdl)
        score = 0.0
        for term, qf_i in query_terms.items():
            f_i = doc.terms.get(term, 0)
            if f_i == 0:
                continue                      # middle factor would be 0
            n_i = df.get(term, 0)
            idf_part = math.log(((r_i + 0.5) / (R - r_i + 0.5))
                                / ((n_i - r_i + 0.5) / (N - n_i - R + r_i + 0.5)))
            tf_part = ((K1 + 1) * f_i) / (K + f_i)
            qf_part = ((K2 + 1) * qf_i) / (K2 + qf_i)
            score += idf_part * tf_part * qf_part
        scores[newsID] = score
    return scores


def main():
    stopwordList = load_stop_words(config.STOPWORDS_FILE)
    coll = Parse_Docs(stopwordList, config.INPUT_FOLDER)
    d_f = df(coll)

    lines = ["IFQ647 Assignment 1 - Question 3 - {} ({})".format(
        config.STUDENT_NAME, config.STUDENT_ID), ""]
    lines.append("BM25 parameters: k1 = {}, k2 = {}, b = {}, R = r_i = 0"
                 .format(K1, K2, B))
    lines.append("Average document length for this collection is: {}"
                 .format(avg_length(coll)))
    lines.append("")

    for query in QUERIES:
        scores = my_bm25(coll, query, d_f, stopwordList)
        lines.append("The query is: {}".format(query))
        for newsID, score in scores.items():
            lines.append("Document ID: {}, Doc Length: {} -- BM25 Score: {}"
                         .format(newsID, coll[newsID].get_doc_size(), score))
        lines.append("")
        lines.append('For query "{}", the top-{} relevant documents are:'
                     .format(query, TOP_N))
        for newsID, score in sort_scores(scores)[:TOP_N]:
            lines.append("{} {}".format(newsID, score))
        lines.append("")

    output = "\n".join(lines)
    print(output)
    with open(config.output_path("Q3"), "w", encoding="utf-8") as file:
        file.write(output)


if __name__ == "__main__":
    main()
