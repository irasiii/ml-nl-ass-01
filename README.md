# ml-nl-ass-01

IFQ647 Machine Learning for Natural Language Processing, Assignment 1:
document and query parsing, a TF\*IDF-based IR model and a BM25-based IR model
over the 15-document RCV1v3 collection.

## Run

```
python q1_parsing.py     # Question 1 -> outputs/<name>_Q1.txt
python q2_tfidf.py       # Question 2 -> outputs/<name>_Q2.txt
python q3_bm25.py        # Question 3 -> outputs/<name>_Q3.txt
python make_submission.py   # runs all three and builds the submission ZIP
```

Set your name and student number in `config.py` first. No third-party packages
are needed to run the code. See `readme.txt` for the user manual.

## Documentation

- [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md): how the solution works, the
  formulas, design decisions, tests and pipeline.
- [docs/HOW_TO.md](docs/HOW_TO.md): step-by-step setup, running, pushing,
  pipeline checks and building the submission ZIP.

## DevSecOps

| Stage | Tool | Where |
|---|---|---|
| Pre-commit checks | ruff, bandit, pytest | `.pre-commit-config.yaml` |
| Secret scanning | gitleaks | `.github/workflows/devsecops.yml` |
| Lint | ruff | workflow |
| Static security analysis | bandit | workflow |
| Dependency audit | pip-audit, Dependabot | workflow, `.github/dependabot.yml` |
| Tests | pytest on Python 3.10 and 3.12 | workflow |
| Build | runs Q1-Q3 and uploads the output files | workflow |

The workflow runs on every push and pull request and weekly, with read-only
permissions. Security-relevant design choices in the code: XML files are read
as plain text (no XML parser, so no entity-expansion attacks), there is no
`eval`, shell call or network access, and all paths come from `config.py`.

Local setup:

```
pip install -r requirements-dev.txt
pre-commit install
```
