IFQ647 Assignment 1 - user manual
Student: Your Full Name (n00000000)

REQUIREMENTS
  Python 3.8 or later. No extra packages are needed: the code uses only the
  standard library and the 'stemming' package supplied with the assignment.

FILES
  config.py          student details and data/output paths (edit name/ID here)
  docv3.py           DocV3 class, Parse_Docs(), Parse_Q()            (Question 1)
  q1_parsing.py      main for Question 1  -> <name>_Q1.txt
  q2_tfidf.py        df(), tfidf(), TF*IDF IR model -> <name>_Q2.txt (Question 2)
  q3_bm25.py         avg_length(), my_bm25(), BM25 IR model -> <name>_Q3.txt
  make_submission.py runs everything and builds the submission ZIP
  data/RCV1v3        the 15 XML documents
  data/common-english-words.txt   stop-word list (unchanged)
  stemming/          Porter2 stemmer supplied with the assignment

HOW TO RUN (PyCharm or VS Code)
  1. Open this folder as the project.
  2. Run q1_parsing.py, then q2_tfidf.py, then q3_bm25.py
     (right-click the file > Run), or from a terminal in this folder:
         python q1_parsing.py
         python q2_tfidf.py
         python q3_bm25.py
  3. Each script prints its results and writes them to the 'outputs' folder
     (in the ZIP the three .txt files are placed at the top level).

NOTES
  - BM25 uses k1 = 1.2, k2 = 100, b = 0.75 and R = r_i = 0.
  - my_bm25() has one extra optional parameter, stop_words, so the stop-word
    file is not re-read for every query.
