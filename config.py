"""
config.py -- shared settings for IFQ647 Assignment 1.

Every script imports its paths and labels from here, so the student details
and the data locations only have to be changed in one place.
"""
import os

# --- Student details (used to label and name the output files) --------------
STUDENT_NAME = "Your Full Name"      # TODO: replace with your full name
STUDENT_ID = "n00000000"             # TODO: replace with your student number

# --- Paths (all relative to this file, so the code runs from any folder) ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_FOLDER = os.path.join(DATA_DIR, "RCV1v3")
STOPWORDS_FILE = os.path.join(DATA_DIR, "common-english-words.txt")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")


def output_path(question):
    """Return the path of an output file, e.g. 'outputs/Your Full Name_Q1.txt'.

    question -- the label 'Q1', 'Q2' or 'Q3'.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return os.path.join(OUTPUT_DIR, "{}_{}.txt".format(STUDENT_NAME, question))
