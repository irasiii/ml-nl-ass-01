# How-to guide

Step-by-step instructions for setting up, running, checking, pushing and
submitting the solution. For an explanation of how the solution works see
[DOCUMENTATION.md](DOCUMENTATION.md).

Commands are for the VS Code terminal on Windows (PowerShell). Open it with
**Ctrl+`**.

## Contents

1. [Install the tools](#1-install-the-tools)
2. [Open the project in VS Code](#2-open-the-project-in-vs-code)
3. [Set your name and student number](#3-set-your-name-and-student-number)
4. [Run the three questions](#4-run-the-three-questions)
5. [Run the tests](#5-run-the-tests)
6. [Run the security and quality checks locally](#6-run-the-security-and-quality-checks-locally)
7. [Push to GitHub](#7-push-to-github)
8. [Check the DevSecOps pipeline](#8-check-the-devsecops-pipeline)
9. [Make a change safely](#9-make-a-change-safely)
10. [Build the submission ZIP](#10-build-the-submission-zip)
11. [Run in PyCharm](#11-run-in-pycharm)
12. [Common tasks](#12-common-tasks)
13. [Troubleshooting](#13-troubleshooting)

## 1. Install the tools

| Tool | Needed for | Check it is installed |
|---|---|---|
| Python 3.8 or later | running the code | `python --version` |
| Git | version control | `git --version` |
| VS Code | editing and running | open it |
| VS Code Python extension | Run button, test panel | Extensions view, search "Python" |

When you open the folder, VS Code offers to install the recommended
extensions (Python and Ruff). Accept.

## 2. Open the project in VS Code

1. Open VS Code.
2. Choose **File > Open Folder**.
3. Select `C:\ML-NL-Assignment 1\ml-nl-ass-01` and click **Select Folder**.
4. If asked whether you trust the authors, choose **Yes**.
5. Press **Ctrl+Shift+P**, type `Python: Select Interpreter`, and pick your
   Python installation.

Optional but recommended: create a virtual environment so the development
tools stay separate from your system Python.

```
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell refuses to run the activation script, run this once and try
again:

```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 3. Set your name and student number

Open `config.py` and change two lines:

```python
STUDENT_NAME = "Your Full Name"      # e.g. "Jane Citizen"
STUDENT_ID = "n00000000"             # e.g. "n12345678"
```

Also change the second line of `readme.txt` to match. The output file names
and the ZIP name are built from these values, and the last word of
`STUDENT_NAME` is used as your surname.

## 4. Run the three questions

From the terminal, in the project folder:

```
python q1_parsing.py
python q2_tfidf.py
python q3_bm25.py
```

Or use the **Run and Debug** panel (**Ctrl+Shift+D**), pick "Q1 parsing",
"Q2 TF\*IDF" or "Q3 BM25" from the drop-down, and press **F5**.

Each script prints its results and writes the same text to the `outputs`
folder:

| Script | Output file |
|---|---|
| `q1_parsing.py` | `outputs/<your name>_Q1.txt` |
| `q2_tfidf.py` | `outputs/<your name>_Q2.txt` |
| `q3_bm25.py` | `outputs/<your name>_Q3.txt` |

Quick check that it worked: the first document block in the Q1 file should
read `Document 741299 contains 96 indexing terms and have total 199 words`.

## 5. Run the tests

Install the development tools once:

```
pip install -r requirements-dev.txt
```

Then run:

```
pytest
```

Expected result: `12 passed`. You can also use the **Testing** panel (the
flask icon) in VS Code to run tests one at a time.

## 6. Run the security and quality checks locally

These are the same checks the pipeline runs on GitHub.

| Check | Command | Passing result |
|---|---|---|
| Lint | `ruff check .` | `All checks passed!` |
| Static security analysis | `bandit -c pyproject.toml -r .` | `No issues identified.` |
| Dependency audit | `pip-audit -r requirements-dev.txt` | `No known vulnerabilities found` |

To run lint, security scan and tests automatically before every commit:

```
pre-commit install
```

After this, `git commit` is blocked if any check fails. Fix the problem and
commit again. To run the hooks by hand: `pre-commit run --all-files`.

## 7. Push to GitHub

The repository is `https://github.com/irasiii/ml-nl-ass-01` (private). The
local folder is already a Git repository with `origin` pointing at it.

**First push.** GitHub created the repository with an automatic README
commit, so the first push must replace it:

```
git push -u origin main --force
```

VS Code opens a browser window to sign in to GitHub if you are not signed in.
Use `--force` only this one time.

**Every push after that:**

```
git add -A
git commit -m "Describe what you changed"
git push
```

Or use the **Source Control** panel (**Ctrl+Shift+G**): type a message,
click **Commit**, then **Sync Changes**.

## 8. Check the DevSecOps pipeline

1. Open the repository on GitHub and click the **Actions** tab.
2. Click the most recent "DevSecOps" run.
3. Four stages should show a green tick:

| Job | Meaning of a red cross |
|---|---|
| Secret scan (gitleaks) | a password, token or key was committed |
| Lint, SAST and dependency audit | a ruff, bandit or pip-audit finding |
| Tests | a unit test failed |
| Build outputs | one of the three scripts crashed |

4. Click a failed job to read its log. Fix the problem locally, commit and
   push; the pipeline runs again.
5. On a successful run, the three generated output files can be downloaded
   from the **Artifacts** section at the bottom of the run page.

If gitleaks reports a real secret, removing it in a new commit is not
enough, because it stays in the history. Change the secret (revoke the token
or password) first, then ask for help rewriting history.

Dependabot opens pull requests when a tool or GitHub Action has an update.
Review them under the **Pull requests** tab and merge the ones whose
pipeline passes.

## 9. Make a change safely

Work on a branch so that `main` always passes:

```
git checkout -b my-change
```

Edit, then check locally:

```
ruff check .
pytest
```

Commit and push the branch:

```
git add -A
git commit -m "Describe the change"
git push -u origin my-change
```

On GitHub, open a pull request from the branch. The pipeline runs on the
pull request. When it is green, merge it, then update your local copy:

```
git checkout main
git pull
```

## 10. Build the submission ZIP

After setting your name and student number (step 3):

```
python make_submission.py
```

This runs all three questions and creates `<studentID>_<Surname>_Asm1.zip`
in the project folder, laid out as the assignment requires:

```
n12345678_Citizen_Asm1.zip
├── Jane Citizen_Q1.txt
├── Jane Citizen_Q2.txt
├── Jane Citizen_Q3.txt
└── Citizen_code/
    ├── config.py, docv3.py, q1_parsing.py, q2_tfidf.py, q3_bm25.py
    ├── make_submission.py, readme.txt
    ├── data/       (RCV1v3 and the stop-word file)
    └── stemming/
```

Before uploading:

1. Open the ZIP and check the three `.txt` files carry your real name.
2. Extract it to a new folder and run the three scripts from the
   `<Surname>_code` folder to confirm they work from the ZIP alone.
3. Upload the ZIP to "Assignment 1: ZIP file submission".
4. Upload the report separately to "Assignment 1: Portfolio". The report is
   not produced by this repository.

ZIP files are ignored by Git, so the submission file is never pushed.

## 11. Run in PyCharm

The tutor tests in PyCharm, so check it works there too.

1. **File > Open**, select the project folder (or the extracted
   `<Surname>_code` folder).
2. Set an interpreter under **File > Settings > Project > Python
   Interpreter**.
3. Right-click `q1_parsing.py` and choose **Run 'q1_parsing'**. Repeat for
   `q2_tfidf.py` and `q3_bm25.py`.

No packages need to be installed.

## 12. Common tasks

| Task | What to change |
|---|---|
| Add or change a Q1 test query | `TEST_QUERIES` in `q1_parsing.py` (keep at least three) |
| Use different titles as Q2 queries | `TITLE_DOC_IDS` in `q2_tfidf.py` (document IDs) |
| Add a free-text Q2 query | `EXTRA_QUERIES` in `q2_tfidf.py` |
| Change the number of terms printed | `TOP_TERMS` in `q2_tfidf.py` |
| Change BM25 parameters | `K1`, `K2`, `B` in `q3_bm25.py` |
| Change the number of ranked results | `TOP_N` in `q3_bm25.py` |
| Use a different document folder | `INPUT_FOLDER` in `config.py` |
| Add a stop word | edit `data/common-english-words.txt`, and add a comment in `docv3.py` describing the change (the assignment requires this) |
| Change the minimum term length | `MIN_TERM_LENGTH` in `docv3.py`, and update the term definition comment |

The four BM25 queries in `QUERIES` are fixed by the assignment; do not
remove any. After any change, run `pytest`. Some tests assert exact values
from the specification (for example 96 terms in document 741299), so a
change to tokenising, stop words or term length will make them fail; update
the expected values only if the change is intended.

## 13. Troubleshooting

| Problem | Cause and fix |
|---|---|
| `python` is not recognised | Python is not on PATH. Try `py` instead of `python`, or reinstall Python with "Add to PATH" ticked. |
| `ModuleNotFoundError: No module named 'stemming'` | The script was run from a copy missing the `stemming` folder. Run from the project folder, with `stemming/` beside the `.py` files. |
| `FileNotFoundError` for the data | The `data` folder is missing or was moved. It must sit beside `config.py`. |
| Output files are named `Your Full Name_Q1.txt` | `config.py` still has the placeholder. See step 3. |
| `pytest` is not recognised | Development tools not installed, or the virtual environment is not active. Run `pip install -r requirements-dev.txt`, or use `python -m pytest`. |
| `git push` is rejected (non-fast-forward) | First push only: use the `--force` command in step 7. Later: run `git pull --rebase`, then push again. |
| `git push` asks for a password and fails | GitHub does not accept account passwords. Sign in through the browser window VS Code opens, or run `gh auth login` if you have the GitHub CLI. |
| Pipeline fails at "Secret scan" | See the note in step 8. |
| Pipeline fails at "Lint" | Run `ruff check .` locally; `ruff check . --fix` repairs most findings. |
| pre-commit blocks a commit | Read the message, fix the finding, `git add` the fix, commit again. |
| Scores differ from the specification's examples | Expected. See section 11 of `DOCUMENTATION.md`. |
