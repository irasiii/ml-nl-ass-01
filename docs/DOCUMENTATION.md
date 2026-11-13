# Solution documentation

IFQ647 Machine Learning for Natural Language Processing, Assignment 1.
This document explains what the solution does, how it is designed, and why.
For step-by-step instructions (setup, running, pushing, submitting) see
[HOW_TO.md](HOW_TO.md).

## Contents

1. [Overview](#1-overview)
2. [Project structure](#2-project-structure)
3. [Data](#3-data)
4. [Question 1: parsing documents and queries](#4-question-1-parsing-documents-and-queries)
5. [Question 2: TF\*IDF-based IR model](#5-question-2-tfidf-based-ir-model)
6. [Question 3: BM25-based IR model](#6-question-3-bm25-based-ir-model)
7. [Function reference](#7-function-reference)
8. [Tests](#8-tests)
9. [DevSecOps pipeline](#9-devsecops-pipeline)
10. [Requirement checklist](#10-requirement-checklist)
11. [Known differences from the specification examples](#11-known-differences-from-the-specification-examples)

## 1. Overview

The solution builds a small information retrieval system over 15 Reuters news
documents (the RCV1v3 collection):

| Question | What it does | Script | Output file |
|---|---|---|---|
| 1 | Parses XML documents and query strings into bags of words | `q1_parsing.py` | `<name>_Q1.txt` |
| 2 | Weights terms with TF\*IDF and ranks documents for a query | `q2_tfidf.py` | `<name>_Q2.txt` |
| 3 | Ranks documents for a query with BM25 | `q3_bm25.py` | `<name>_Q3.txt` |

The code uses only the Python standard library and the `stemming` package
supplied with the assignment data. It runs on Python 3.8 or later.

Data flows in one direction:

```
XML files + stop words
        |
        v
  Parse_Docs()  ->  {newsID: DocV3}  ----+--> df()  -> {term: df}
                                         |              |
  query string -> Parse_Q() -> {term: qf}|              v
                         |               +--> tfidf() -> rank_tfidf()  (Q2)
                         |               |
                         +---------------+--> my_bm25()                (Q3)
```

## 2. Project structure

```
ml-nl-ass-01/
├── config.py               student details, data and output paths
├── docv3.py                DocV3 class, Parse_Docs, Parse_Q (Question 1)
├── q1_parsing.py           main for Question 1
├── q2_tfidf.py             df, tfidf, TF*IDF IR model (Question 2)
├── q3_bm25.py              avg_length, my_bm25, BM25 IR model (Question 3)
├── make_submission.py      runs everything and builds the submission ZIP
├── readme.txt              short user manual required in the ZIP
├── data/
│   ├── RCV1v3/             the 15 XML documents
│   └── common-english-words.txt   stop-word list (unchanged)
├── stemming/               Porter2 stemmer supplied with the assignment
├── tests/test_ir.py        unit tests
├── docs/                   this documentation and the how-to guide
├── outputs/                generated .txt files (not committed)
├── .github/                CI workflow and Dependabot settings
├── .pre-commit-config.yaml local checks before each commit
├── pyproject.toml          ruff, bandit and pytest settings
├── requirements-dev.txt    development tools only
└── .vscode/                run configurations and test settings
```

`config.py` holds every path, built relative to its own location, so the
scripts work no matter which folder they are started from.

## 3. Data

Each document is one XML file. The parts the solution uses are:

```xml
<newsitem itemid="741299" id="root" date="1997-07-20" xml:lang="en">
<title>BELGIUM: MOTOR RACING-LEHTO AND SOPER HOLD ON FOR GT VICTORY.</title>
...
<text>
<p>J.J. Lehto of Finland and Steve Soper of Britain drove ...</p>
</text>
```

- `itemid` becomes the document ID (`newsID`).
- The `<p>` lines between `<text>` and `</text>` are tokenised.
- `<title>` is used only in Question 2, as a source of test queries.

The collection has 15 documents, 1068 distinct terms, and an average length
of 362.6 words. Some documents are duplicates of each other (86961 and 86042;
80483, 80484 and 80884), so tied scores in the rankings are expected.

The stop-word file is a single comma-separated line of 119 common English
words. It is used unchanged.

## 4. Question 1: parsing documents and queries

### 4.1 Definitions of word and term

These definitions are also written as comments at the top of `docv3.py`,
as Task 1.1 requires.

**Word.** A word is a maximal run of English letters found in the text after
(1) XML tags are removed, (2) digits are deleted and (3) every punctuation
character is replaced by a space. Every word counts towards the document
length, including stop words.

| Raw text | Words |
|---|---|
| `fuel-efficient` | `fuel`, `efficient` |
| `car's` | `car`, `s` |
| `16-point` | `point` |
| `1997` | (none) |
| `&quot;I` | `quot`, `I` |

**Term.** A term is the index form of a word: the word is lower-cased and
stemmed with Porter2, and kept only if the stem has more than two characters
and is not a stop word. For example `Ranks` and `ranking` both become `rank`.

XML character entities are not decoded, so `&quot;` produces the term `quot`.
This matches the sample output in the specification.

### 4.2 The DocV3 class

| Member | Purpose |
|---|---|
| `newsID` | document ID from `itemid` |
| `terms` | dictionary `{term: frequency}` |
| `doc_size` | document length: the total number of words |
| `add_term(term)` | adds a term, or adds 1 to its frequency |
| `getNewsID()` | returns the document ID |
| `get_termList()` | returns the terms sorted alphabetically |
| `get_sorted_terms()` | returns `(term, freq)` pairs, highest frequency first |
| `get_doc_size()` / `set_doc_size(n)` | accessor and mutator required by Task 3.1 |

### 4.3 Parse_Docs(stop_words, inputfolder)

For each `.xml` file in the folder, in file-name order:

1. Read the file line by line as plain text (encoding `iso-8859-1`, as
   declared in the XML header).
2. Take `newsID` from the `<newsitem ...>` line.
3. Between `<text>` and `</text>`, strip the `<p>` tags and tokenise each
   line with `tokenize()`.
4. Count every word. Pass each word to `make_term()`; if a term comes back,
   call `doc.add_term(term)`.
5. Store the word count with `doc.set_doc_size()`.

It returns a dictionary `{newsID: DocV3}`.

The files are read as text rather than with an XML library. This follows the
workshop approach, and it also means the parser cannot be attacked through
XML features such as entity expansion.

### 4.4 Parse_Q(query, stop_words)

The query goes through exactly the same `tokenize()` and `make_term()`
functions as the documents, so the two can never drift apart. The result is a
dictionary `{term: frequency}`.

```
'US EPA ranks Geo Metro car most fuel-efficient 1997 car.'
-> {'epa': 1, 'rank': 1, 'geo': 1, 'metro': 1, 'car': 2, 'fuel': 1, 'effici': 1}
```

`US` is dropped because its stem `us` has only two characters (it is also a
stop word), `most` is a stop word, and `1997` is not a word.

### 4.5 Main function (Task 1.3)

`q1_parsing.py` parses the collection, prints one block per document (ID,
number of terms, number of words, then `term : freq` sorted by frequency),
then prints three parsed test queries. The same text is saved to the Q1
output file.

## 5. Question 2: TF\*IDF-based IR model

### 5.1 Document frequency: df(coll)

`df` returns `{term: n}` where `n` is the number of documents that contain
the term. Each document counts once per term, however often the term occurs
in it.

### 5.2 TF\*IDF weights: tfidf(doc, d_f, ndocs)

Equation (1), with natural logarithms:

```
          (log(f_ik) + 1) * log(N / n_k)
d_ik = ------------------------------------------------
       sqrt( sum_x [ (log(f_ix) + 1) * log(N / n_x) ]^2 )
```

| Symbol | Meaning |
|---|---|
| `f_ik` | frequency of term k in document i |
| `N` | number of documents (15) |
| `n_k` | document frequency of term k |

The numerator rewards terms that are frequent in the document and rare in
the collection. The denominator is the length of the document's weight
vector, so after division every document vector has length 1 and long
documents are not favoured.

`doc` may be a `DocV3` object or a plain `{term: freq}` dictionary.

### 5.3 Ranking: rank_tfidf(query_terms, doc_weights)

Equation (2), the abstract model of ranking:

```
R(Q, D) = sum over query terms i of  g_i(Q) * f_i(D)
```

- `g_i(Q)` is the frequency of term i in the parsed query.
- `f_i(D)` is the TF\*IDF weight of term i in document D, or 0 if absent.

### 5.4 Cosine similarity observation

The assignment asks whether ranking by cosine similarity would give similar
results. `q2_tfidf.py` computes both rankings for every query and prints them
side by side.

Result: the document order is identical for every query. The reason is that
Eq. (1) already normalises each document vector to length 1 (the output file
shows all magnitudes are 1 to within rounding). Cosine similarity is then the
abstract score divided by the query vector's length, and that divisor is the
same for every document. The scores shrink, but the order cannot change.

### 5.5 Main function (Task 2.3)

`q2_tfidf.py` prints the document frequencies, then the top 25 TF\*IDF terms
of each document, then the ranking of all 15 documents for four queries:
three document titles and the specification's example query.

| Query source | Query |
|---|---|
| Title of 86961 | USA: EPA ranks Geo Metro most fuel-efficient 1997 car. |
| Title of 741299 | BELGIUM: MOTOR RACING-LEHTO AND SOPER HOLD ON FOR GT VICTORY. |
| Title of 809481 | CANADA: Sherritt to buy Dynatec, spin off unit. |
| Specification example | US EPA ranks Geo Metro car most fuel-efficient 1997 car. |

## 6. Question 3: BM25-based IR model

### 6.1 Average document length: avg_length(coll)

Sums `get_doc_size()` over all documents and divides by the number of
documents. For this collection the result is 362.6 words.

### 6.2 BM25 score: my_bm25(coll, q, df)

Equation (3), with natural logarithms, summed over the query terms:

```
       (r_i + 0.5) / (R - r_i + 0.5)             (k1 + 1) f_i     (k2 + 1) qf_i
log ----------------------------------------- * -------------- * ---------------
    (n_i - r_i + 0.5) / (N - n_i - R + r_i + 0.5)    K + f_i         k2 + qf_i

K = k1 * ((1 - b) + b * dl / avdl)
```

| Symbol | Meaning | Value used |
|---|---|---|
| `R`, `r_i` | relevance information | 0 (none available) |
| `N` | number of documents | 15 |
| `n_i` | document frequency of term i | from `df()` |
| `f_i` | frequency of term i in the document | from `DocV3.terms` |
| `qf_i` | frequency of term i in the query | from `Parse_Q()` |
| `dl`, `avdl` | document length, average length | `doc_size`, `avg_length()` |
| `k1` | term-frequency saturation | 1.2 |
| `k2` | query term-frequency effect | 100 |
| `b` | length normalisation strength | 0.75 |

The specification does not fix `k1`, `k2` and `b`; the values above are the
typical ones from the lecture notes and are printed at the top of the Q3
output.

Two behaviours are worth knowing:

- A query term that is absent from a document contributes 0, because `f_i`
  is 0.
- With `R = r_i = 0` the first factor reduces to
  `log((N - n_i + 0.5) / (n_i + 0.5))`. This is negative for a term that
  appears in more than half the documents (8 or more of 15), so such a term
  lowers the score of documents that contain it.

`my_bm25` has one extra optional parameter, `stop_words`. If it is omitted
the stop-word file is loaded, so the function can still be called exactly as
`my_bm25(coll, q, df)`.

### 6.3 Main function (Task 3.3)

`q3_bm25.py` prints the average document length, then for each of the four
required queries the score of every document and the top five.

| Query | Top document | Score |
|---|---|---|
| The British-Fashion Awards | 783802 | 11.00 |
| Rocket attacks | 809495 | 7.52 |
| Broadcast Fashion Awards | 783802 | 10.01 |
| US EPA ranks Geo Metro car most fuel-efficient 1997 car. | 86042 and 86961 (tie) | 13.78 |

For "Rocket attacks" only one document has a non-zero score, so the other
four places in the top five are filled by documents scoring 0.

## 7. Function reference

| File | Function | Returns |
|---|---|---|
| `config.py` | `output_path(question)` | path of the output file for `'Q1'`, `'Q2'` or `'Q3'` |
| `docv3.py` | `load_stop_words(stopwords_file)` | list of stop words |
| | `tokenize(text)` | list of words |
| | `make_term(word, stop_words)` | the term, or `None` if ignored |
| | `Parse_Docs(stop_words, inputfolder)` | `{newsID: DocV3}` |
| | `Parse_Q(query, stop_words)` | `{term: freq}` |
| | `read_titles(inputfolder)` | `{newsID: title}` |
| `q2_tfidf.py` | `df(coll)` | `{term: df}` |
| | `tfidf(doc, d_f, ndocs)` | `{term: weight}` |
| | `rank_tfidf(query_terms, doc_weights)` | `{newsID: score}` |
| | `cosine(query_terms, weights)` | cosine similarity (a number) |
| | `sort_scores(scores)` | `[(key, score), ...]`, highest first |
| `q3_bm25.py` | `avg_length(coll)` | average document length |
| | `my_bm25(coll, q, df, stop_words=None)` | `{newsID: bm25_score}` |

Functions not named in the specification (`tokenize`, `make_term`,
`load_stop_words`, `read_titles`, `rank_tfidf`, `cosine`, `sort_scores`,
`get_sorted_terms`) each have a docstring in the code explaining what they
are and why they were added.

## 8. Tests

`tests/test_ir.py` contains 12 unit tests, run with `pytest`:

| Area | What is checked |
|---|---|
| `DocV3` | `add_term`, the `doc_size` accessor and mutator, `get_termList` |
| `Parse_Docs` | 15 documents; document 741299 has 96 terms and 199 words, as in the specification |
| Terms | no stop words, no terms shorter than three letters, all lower-case letters |
| `Parse_Q` | the specification's example query; empty and hostile input |
| `df` | `corp` appears in 9 documents; no value exceeds the collection size |
| `tfidf` | every document vector has length 1; accepts a plain dictionary |
| Ranking | TF\*IDF and cosine give the same order; expected top documents |
| `avg_length` | 362.6; empty collection returns 0 |
| `my_bm25` | expected top documents; unknown query scores 0 everywhere |

## 9. DevSecOps pipeline

DevSecOps means security checks run automatically alongside build and test,
from the developer's machine through to the shared repository.

| Stage | Tool | What it catches | Where |
|---|---|---|---|
| Before commit | pre-commit (ruff, bandit, pytest) | problems before they enter history | `.pre-commit-config.yaml` |
| Secret scan | gitleaks | passwords, tokens or keys committed by mistake, across full history | workflow job `secrets` |
| Lint | ruff | errors, unused code, risky patterns | workflow job `quality-and-security` |
| Static security analysis | bandit | insecure Python constructs | same job |
| Dependency audit | pip-audit | known vulnerabilities in the development tools | same job |
| Dependency updates | Dependabot | outdated packages and GitHub Actions, weekly | `.github/dependabot.yml` |
| Test | pytest on Python 3.10 and 3.12 | incorrect results | workflow job `test` |
| Build | runs Q1 to Q3 | scripts that fail to run; uploads the three output files | workflow job `build` |

The workflow (`.github/workflows/devsecops.yml`) runs on every push to
`main`, on every pull request, and once a week. Jobs are gated: tests run
only if the security jobs pass, and the build runs only if the tests pass.
The workflow has read-only access to the repository.

Security choices in the code itself:

- XML is read as plain text, so XML parser attacks do not apply.
- No `eval`, `exec`, shell commands or network access.
- All file paths come from `config.py`; none are built from user input.
- No third-party runtime dependencies, so there is no supply chain to
  compromise at run time. The supplied `stemming` package is excluded from
  linting because it is not our code.
- The repository is private, and generated outputs and ZIP files are not
  committed.

## 10. Requirement checklist

| Requirement | Where it is met |
|---|---|
| `DocV3` with `newsID`, `terms`, `doc_size`, `add_term()` | `docv3.py` |
| Accessor and mutator for `doc_size` | `get_doc_size`, `set_doc_size` |
| Word and term definitions as comments | top of `docv3.py` |
| Stop words read into `stopwordList` | `load_stop_words`, used in each main |
| Identical tokenising for documents and queries | shared `tokenize` and `make_term` |
| `Parse_Q` tested on three queries | `q1_parsing.py` |
| Q1 output file | `q1_parsing.py` |
| `df()` and `tfidf()` using Eq. (1), natural log | `q2_tfidf.py` |
| Top 25 terms per document | `q2_tfidf.py` |
| TF\*IDF IR model with Eq. (2), at least three titles, sorted descending | `q2_tfidf.py` |
| Cosine similarity observation | end of the Q2 output, and section 5.4 |
| `avg_length()` and `my_bm25()` using Eq. (3), `R = r_i = 0` | `q3_bm25.py` |
| Four required queries, top 5 each | `q3_bm25.py` |
| `readme.txt` user manual | `readme.txt` |
| ZIP named `studentID_Surname_Asm1.zip` | `make_submission.py` |
| Report of 9 pages | not part of this repository |

## 11. Known differences from the specification examples

The specification says outputs need not match its examples exactly. The
differences are:

| Item | Specification example | This solution |
|---|---|---|
| Document 741299 | 96 terms, 199 words | 96 terms, 199 words (identical) |
| Parsed example query | 7 terms | identical |
| Distinct terms in collection | 1067 | 1068 |
| Terms in document 80483 | 241 | 242 |
| TF\*IDF top score, example query | 0.9108 | 0.9104 |
| BM25 top score, example query | 8.05 | 13.78 |

The one-term differences come from small tokenising or stemming details that
the specification leaves to the student. The BM25 difference comes from the
parameter values, which the specification does not state; the document order
is the same.
