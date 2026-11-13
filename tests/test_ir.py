"""Unit tests for the parsing, TF*IDF and BM25 functions (run with pytest)."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # noqa: E402
from docv3 import DocV3, Parse_Docs, Parse_Q, load_stop_words  # noqa: E402
from q2_tfidf import cosine, df, rank_tfidf, sort_scores, tfidf  # noqa: E402
from q3_bm25 import avg_length, my_bm25  # noqa: E402

STOP = load_stop_words(config.STOPWORDS_FILE)
COLL = Parse_Docs(STOP, config.INPUT_FOLDER)
DF = df(COLL)
EPA_QUERY = "US EPA ranks Geo Metro car most fuel-efficient 1997 car."


def test_docv3_add_term_and_size():
    doc = DocV3("1")
    doc.add_term("car")
    doc.add_term("car")
    doc.add_term("fuel")
    doc.set_doc_size(7)
    assert doc.terms == {"car": 2, "fuel": 1}
    assert doc.get_doc_size() == 7
    assert doc.get_termList() == ["car", "fuel"]


def test_parse_docs_matches_spec_example():
    assert len(COLL) == 15
    doc = COLL["741299"]
    assert len(doc.terms) == 96
    assert doc.get_doc_size() == 199
    assert doc.terms["quot"] == 4
    assert doc.terms["car"] == 3


def test_no_stop_words_or_short_terms_indexed():
    for doc in COLL.values():
        for term in doc.terms:
            assert term not in STOP
            assert len(term) > 2
            assert term.isalpha() and term == term.lower()


def test_parse_q_matches_spec_example():
    assert Parse_Q(EPA_QUERY, STOP) == {
        "epa": 1, "rank": 1, "geo": 1, "metro": 1, "car": 2, "fuel": 1, "effici": 1}


def test_parse_q_handles_empty_and_hostile_input():
    assert Parse_Q("", STOP) == {}
    assert Parse_Q("1997 !!! <script>", STOP) == {"script": 1}
    assert Parse_Q("../../etc/passwd", STOP) == {"etc": 1, "passwd": 1}


def test_df_counts_documents_not_occurrences():
    assert DF["corp"] == 9
    assert max(DF.values()) <= len(COLL)
    assert all(DF[t] >= 1 for doc in COLL.values() for t in doc.terms)


def test_tfidf_vectors_are_unit_length():
    for doc in COLL.values():
        weights = tfidf(doc, DF, len(COLL))
        assert math.isclose(sum(w * w for w in weights.values()), 1.0, rel_tol=1e-9)


def test_tfidf_accepts_plain_dictionary():
    doc = COLL["741299"]
    assert tfidf(doc.terms, DF, len(COLL)) == tfidf(doc, DF, len(COLL))


def test_tfidf_ranking_and_cosine_agree():
    weights = {n: tfidf(d, DF, len(COLL)) for n, d in COLL.items()}
    q = Parse_Q(EPA_QUERY, STOP)
    ranking = sort_scores(rank_tfidf(q, weights))
    cos = sort_scores({n: cosine(q, w) for n, w in weights.items()})
    assert {ranking[0][0], ranking[1][0]} == {"86961", "86042"}
    assert [n for n, _ in ranking] == [n for n, _ in cos]


def test_avg_length():
    assert math.isclose(avg_length(COLL), 362.6)
    assert avg_length({}) == 0


def test_bm25_top_documents():
    scores = my_bm25(COLL, EPA_QUERY, DF, STOP)
    assert len(scores) == len(COLL)
    top = sort_scores(scores)[:2]
    assert {top[0][0], top[1][0]} == {"86961", "86042"}
    assert sort_scores(my_bm25(COLL, "Rocket attacks", DF, STOP))[0][0] == "809495"


def test_bm25_unknown_query_scores_zero():
    assert set(my_bm25(COLL, "zzzzqqqq", DF, STOP).values()) == {0.0}
