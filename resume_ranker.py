"""
Resume Ranking System
---------------------
Ranks candidates based on their relevance to a given job description
using TF-IDF vectorization and Cosine Similarity.
Supports: .txt, .pdf, .docx files
"""

import os
import re
import csv
import string
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ── NLTK setup ──────────────────────────────────────────
def download_nltk_data():
    for resource in ['punkt', 'stopwords', 'wordnet', 'omw-1.4', 'punkt_tab']:
        try:
            nltk.download(resource, quiet=True)
        except Exception:
            pass

download_nltk_data()


# ── FILE READING ─────────────────────────────────────────

def read_txt(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def read_pdf(filepath: str) -> str:
    try:
        import PyPDF2
        text = []
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return '\n'.join(text)
    except Exception as e:
        return f"[PDF read error: {e}]"


def read_docx(filepath: str) -> str:
    try:
        from docx import Document
        doc = Document(filepath)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return '\n'.join(paragraphs)
    except Exception as e:
        return f"[DOCX read error: {e}]"


def load_text_file(filepath: str) -> str:
    """Auto-detect file type and extract text."""
    ext = Path(filepath).suffix.lower()
    if ext == '.pdf':
        return read_pdf(filepath)
    elif ext in ('.docx', '.doc'):
        return read_docx(filepath)
    else:
        return read_txt(filepath)


# ── TEXT PREPROCESSING ───────────────────────────────────

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation + string.digits))
    try:
        tokens = word_tokenize(text)
    except Exception:
        tokens = text.split()
    try:
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        tokens = [
            lemmatizer.lemmatize(token)
            for token in tokens
            if token not in stop_words and len(token) > 2
        ]
    except Exception:
        tokens = [t for t in tokens if len(t) > 2]
    return ' '.join(tokens)


# ── KEYWORD EXTRACTION ───────────────────────────────────

def extract_keywords(text: str, top_n: int = 15) -> list:
    try:
        vectorizer = TfidfVectorizer(max_features=top_n, stop_words='english')
        vectorizer.fit_transform([text])
        return vectorizer.get_feature_names_out().tolist()
    except Exception:
        return list(set(text.split()))[:top_n]


# ── CANDIDATE NAME EXTRACTION ────────────────────────────

def extract_candidate_name(text: str, filename: str) -> str:
    lines = text.strip().split('\n')
    for line in lines[:8]:
        line = line.strip()
        if line.lower().startswith('name:'):
            name = line.split(':', 1)[1].strip()
            if name:
                return name
        words = line.split()
        if 2 <= len(words) <= 4 and all(w.replace('.','').isalpha() for w in words):
            return line
    return Path(filename).stem.replace('_', ' ').replace('-', ' ').title()


# ── SUPPORTED FILE TYPES ─────────────────────────────────

SUPPORTED_EXTENSIONS = {'.txt', '.pdf', '.docx', '.doc'}


def get_resume_files(folder: str) -> list:
    return [
        f for f in os.listdir(folder)
        if Path(f).suffix.lower() in SUPPORTED_EXTENSIONS
    ]


# ── CORE RANKING ENGINE ──────────────────────────────────

def rank_resumes(
    job_desc_path: str,
    resumes_folder: str,
    export_csv: bool = True,
    output_csv: str = "ranking_results.csv"
) -> pd.DataFrame:

    job_desc_raw   = load_text_file(job_desc_path)
    job_desc_clean = preprocess_text(job_desc_raw)

    resume_files = get_resume_files(resumes_folder)
    if not resume_files:
        raise ValueError(f"No supported resume files found in: {resumes_folder}\nSupported: .txt, .pdf, .docx")

    candidates  = []
    raw_texts   = []

    for fname in resume_files:
        fpath    = os.path.join(resumes_folder, fname)
        raw_text = load_text_file(fpath)
        name     = extract_candidate_name(raw_text, fname)
        clean    = preprocess_text(raw_text)
        candidates.append({'name': name, 'filename': fname})
        raw_texts.append(clean)

    all_texts  = [job_desc_clean] + raw_texts
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_df=0.95, min_df=1, sublinear_tf=True)
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    job_vector     = tfidf_matrix[0]
    resume_vectors = tfidf_matrix[1:]
    similarities   = cosine_similarity(job_vector, resume_vectors)[0]

    results = []
    for i, candidate in enumerate(candidates):
        score = float(similarities[i])
        results.append({
            'Candidate Name':    candidate['name'],
            'Filename':          candidate['filename'],
            'File Type':         Path(candidate['filename']).suffix.upper().replace('.',''),
            'Match Score (Raw)': round(score, 4),
            'Match Percentage':  f"{round(score * 100, 2)}%",
        })

    df = pd.DataFrame(results)
    df = df.sort_values('Match Score (Raw)', ascending=False).reset_index(drop=True)
    df.insert(0, 'Rank', range(1, len(df) + 1))

    if export_csv:
        df[['Rank', 'Candidate Name', 'Match Percentage']].to_csv(output_csv, index=False)

    return df


# ── CLI ──────────────────────────────────────────────────

def print_results(df: pd.DataFrame):
    print("\n" + "="*55)
    print("        RESUME RANKING RESULTS")
    print("="*55)
    print(f"{'Rank':<6} {'Candidate Name':<25} {'Match Score':<15}")
    print("-"*55)
    for _, row in df.iterrows():
        print(f"{int(row['Rank']):<6} {row['Candidate Name']:<25} {row['Match Percentage']:<15}")
    print("="*55)


if __name__ == "__main__":
    import sys
    base_dir   = Path(__file__).parent
    job_desc   = str(base_dir / "job_description.txt")
    resumes_dir = str(base_dir / "resumes")
    output_csv = str(base_dir / "ranking_results.csv")

    if len(sys.argv) >= 3:
        job_desc    = sys.argv[1]
        resumes_dir = sys.argv[2]

    df = rank_resumes(job_desc, resumes_dir, export_csv=True, output_csv=output_csv)
    print_results(df)
