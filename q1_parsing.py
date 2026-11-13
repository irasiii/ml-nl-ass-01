"""
q1_parsing.py -- Question 1, Task 1.3: test Parse_Docs() and Parse_Q().

Run this file directly.  It prints the results and saves the same text to
'outputs/<your full name>_Q1.txt'.
"""
import config
from docv3 import Parse_Docs, Parse_Q, load_stop_words

# Three test queries for Task 1.2 (the first is the example in the spec).
TEST_QUERIES = [
    "US EPA ranks Geo Metro car most fuel-efficient 1997 car.",
    "BELGIUM: MOTOR RACING-LEHTO AND SOPER HOLD ON FOR GT VICTORY.",
    "The British-Fashion Awards",
]


def main():
    stopwordList = load_stop_words(config.STOPWORDS_FILE)
    coll = Parse_Docs(stopwordList, config.INPUT_FOLDER)

    lines = ["IFQ647 Assignment 1 - Question 1 - {} ({})".format(
        config.STUDENT_NAME, config.STUDENT_ID), ""]

    # Task 1.1 output: one block per document.
    for newsID, doc in coll.items():
        lines.append("Document {} contains {} indexing terms and have total "
                     "{} words".format(newsID, len(doc.terms), doc.get_doc_size()))
        for term, freq in doc.get_sorted_terms():
            lines.append("{} : {}".format(term, freq))
        lines.append("")

    # Task 1.2 output: parsed queries.
    for query in TEST_QUERIES:
        lines.append("Query: {}".format(query))
        lines.append("The parsed query:")
        lines.append(str(Parse_Q(query, stopwordList)))
        lines.append("")

    output = "\n".join(lines)
    print(output)
    with open(config.output_path("Q1"), "w", encoding="utf-8") as file:
        file.write(output)


if __name__ == "__main__":
    main()
