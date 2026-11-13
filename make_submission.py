"""
make_submission.py -- build the ZIP file for the 'Assignment 1: ZIP file' link.

Runs the three question scripts, then creates
'<studentID>_<Surname>_Asm1.zip' containing the three output .txt files and a
'<Surname>_code' folder with every .py file, the data and readme.txt.
"""
import os
import zipfile

import config
import q1_parsing
import q2_tfidf
import q3_bm25

CODE_ITEMS = ["config.py", "docv3.py", "q1_parsing.py", "q2_tfidf.py",
              "q3_bm25.py", "make_submission.py", "readme.txt", "data",
              "stemming"]


def main():
    for module in (q1_parsing, q2_tfidf, q3_bm25):
        module.main()

    surname = config.STUDENT_NAME.split()[-1]
    zip_name = "{}_{}_Asm1.zip".format(config.STUDENT_ID, surname)
    code_folder = "{}_code".format(surname)
    zip_path = os.path.join(config.BASE_DIR, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for question in ("Q1", "Q2", "Q3"):
            path = config.output_path(question)
            archive.write(path, os.path.basename(path))
        for item in CODE_ITEMS:
            full = os.path.join(config.BASE_DIR, item)
            if os.path.isfile(full):
                archive.write(full, os.path.join(code_folder, item))
                continue
            for root, _dirs, files in os.walk(full):
                for name in files:
                    if name.endswith((".pyc", ".pyo")):
                        continue
                    file_path = os.path.join(root, name)
                    rel = os.path.relpath(file_path, config.BASE_DIR)
                    archive.write(file_path, os.path.join(code_folder, rel))
    print("\nCreated {}".format(zip_path))


if __name__ == "__main__":
    main()
