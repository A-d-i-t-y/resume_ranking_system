# 🎯 Task 1: Intelligent Resume Ranking System

AI-powered resume shortlisting using **TF-IDF** and **Cosine Similarity**.

---

## 🚀 Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run Streamlit app
streamlit run app.py

# 3. OR run CLI version
python resume_ranker.py
```

---

## 📁 Project Structure

```
task1_resume_ranking/
│
├── app.py                  # Streamlit UI (frontend + backend integration)
├── resume_ranker.py        # Core ranking engine (TF-IDF + Cosine Similarity)
├── requirements.txt
├── job_description.txt     # Sample job description
├── ranking_results.csv     # Auto-generated output
│
└── resumes/                # Folder with candidate resumes (.txt)
    ├── priya_sharma.txt
    ├── sneha_patel.txt
    ├── aman_verma.txt
    ├── ananya_roy.txt
    ├── rahul_gupta.txt
    └── vikram_singh.txt
```

---

## ⚙️ How It Works

| Step | Technique | Purpose |
|------|-----------|---------|
| 1 | Text Cleaning | Remove URLs, emails, punctuation, digits |
| 2 | Tokenization | Split into words using NLTK |
| 3 | Stopword Removal | Remove noise words (the, is, a…) |
| 4 | Lemmatization | Normalize forms: running → run |
| 5 | TF-IDF Vectorization | Convert text to numerical vectors |
| 6 | Cosine Similarity | Score each resume vs. job description |
| 7 | Ranking | Sort by descending similarity score |

**Cosine Similarity Formula:**

```
similarity(A, B) = (A · B) / (||A|| × ||B||)
```

---

## ✅ Features

- [x] Text preprocessing (cleaning, tokenization, stopword removal, lemmatization)
- [x] TF-IDF vectorization with bigrams
- [x] Cosine similarity scoring
- [x] Ranked output (highest to lowest)
- [x] CSV export
- [x] Streamlit UI with charts (bar + pie)
- [x] Demo mode + file upload mode
- [x] Keyword extraction & analysis tab

---

## 📊 Sample Output

| Rank | Candidate | Match Score |
|------|-----------|-------------|
| 1 | Priya Sharma | 18.09% |
| 2 | Sneha Patel | 15.96% |
| 3 | Aman Verma | 12.42% |
| 4 | Ananya Roy | 11.49% |
| 5 | Rahul Gupta | 10.54% |
| 6 | Vikram Singh | 2.67% |

---

## 📝 Usage — Upload Your Own Files

1. Open app → sidebar → select **"Upload Your Files"**
2. Upload your `.txt` job description
3. Upload 2+ `.txt` resume files
4. Click **Rank Candidates**
5. Download results as CSV

---

Built for **CampusPull AI Intern Assessment 2025**
