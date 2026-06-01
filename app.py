"""
Resume Ranking System — Streamlit App
Supports: .txt  |  .pdf  |  .docx / .doc
Run: streamlit run app.py
"""

import os
import tempfile
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from resume_ranker import (
    rank_resumes, preprocess_text, extract_keywords,
    load_text_file, SUPPORTED_EXTENSIONS
)

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="Resume Ranking System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
[data-testid="stToolbar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 1.4rem !important; }
.stApp { background: #f0f2f6; }

.hero {
    background: linear-gradient(135deg, #0a0e27 0%, #1a1a4e 45%, #0d2b6b 75%, #0a4a8f 100%);
    border-radius: 18px; padding: 2.4rem 2rem; margin-bottom: 1.8rem;
    position: relative; overflow: hidden;
    box-shadow: 0 10px 40px rgba(10,14,39,0.35);
}
.hero::before {
    content:""; position:absolute; inset:0;
    background: radial-gradient(ellipse at 80% 20%, rgba(99,179,237,0.18) 0%, transparent 60%),
                radial-gradient(ellipse at 10% 80%, rgba(128,90,213,0.15) 0%, transparent 55%);
}
.hero-title {
    font-family:'Space Grotesk',sans-serif; font-size:2.3rem; font-weight:700;
    color:#fff; margin:0; position:relative; text-shadow:0 2px 12px rgba(0,0,0,.3);
}
.hero-sub { color:rgba(255,255,255,.72); font-size:1rem; margin-top:.45rem; position:relative; }
.hero-badge {
    display:inline-block; background:rgba(255,255,255,.12);
    border:1px solid rgba(255,255,255,.22); color:#93c5fd;
    font-size:.75rem; font-weight:600; letter-spacing:.08em; text-transform:uppercase;
    padding:4px 13px; border-radius:20px; margin:10px 6px 0 0; position:relative;
}

.stat-card {
    background:white; border-radius:14px; padding:1.2rem 1.4rem;
    box-shadow:0 2px 12px rgba(0,0,0,.07); text-align:center;
    border-top:4px solid transparent; transition:transform .2s,box-shadow .2s;
}
.stat-card:hover { transform:translateY(-3px); box-shadow:0 8px 24px rgba(0,0,0,.12); }
.stat-card.blue   { border-top-color:#3b82f6; }
.stat-card.green  { border-top-color:#10b981; }
.stat-card.purple { border-top-color:#8b5cf6; }
.stat-val { font-family:'Space Grotesk',sans-serif; font-size:1.9rem; font-weight:700; color:#1e293b; }
.stat-lbl { font-size:.8rem; color:#64748b; font-weight:500; text-transform:uppercase; letter-spacing:.05em; margin-top:2px; }

.rank-row {
    background:white; border-radius:12px; padding:.95rem 1.4rem; margin:.5rem 0;
    box-shadow:0 2px 8px rgba(0,0,0,.06);
    border-left:5px solid #e2e8f0; transition:transform .15s,box-shadow .15s;
    display:flex; align-items:center; gap:1rem;
}
.rank-row:hover { transform:translateX(4px); box-shadow:0 4px 16px rgba(0,0,0,.1); }
.rank-row.gold   { border-left-color:#f59e0b; background:linear-gradient(90deg,#fffbeb 0%,white 30%); }
.rank-row.silver { border-left-color:#94a3b8; background:linear-gradient(90deg,#f8fafc 0%,white 30%); }
.rank-row.bronze { border-left-color:#d97706; background:linear-gradient(90deg,#fffaf0 0%,white 30%); }
.rank-medal { font-size:1.6rem; min-width:38px; text-align:center; }
.rank-name  { font-weight:600; font-size:1rem; color:#1e293b; flex:1; }
.rank-score { font-family:'Space Grotesk',sans-serif; font-size:1.3rem; font-weight:700; color:#3b82f6; min-width:68px; text-align:right; }
.rank-badge {
    font-size:.7rem; font-weight:600; padding:2px 9px; border-radius:10px;
    letter-spacing:.04em; text-transform:uppercase;
}
.badge-pdf  { background:#fee2e2; color:#dc2626; }
.badge-docx { background:#dbeafe; color:#2563eb; }
.badge-txt  { background:#dcfce7; color:#16a34a; }
.badge-doc  { background:#ede9fe; color:#7c3aed; }

.stProgress > div > div > div { background:linear-gradient(90deg,#3b82f6,#8b5cf6) !important; border-radius:4px !important; }

.chip { display:inline-block; background:#eff6ff; color:#2563eb; border:1px solid #bfdbfe; border-radius:20px; padding:4px 12px; margin:3px; font-size:.8rem; font-weight:500; }
.chip.jd { background:#f0fdf4; color:#16a34a; border-color:#bbf7d0; }

.sec-hdr { font-family:'Space Grotesk',sans-serif; font-size:1.2rem; font-weight:700; color:#1e293b; margin:1.4rem 0 .75rem; }

.algo-step { display:flex; align-items:flex-start; gap:.9rem; background:white; border-radius:10px; padding:.85rem 1.1rem; margin-bottom:.55rem; box-shadow:0 1px 6px rgba(0,0,0,.06); }
.algo-num { background:linear-gradient(135deg,#3b82f6,#8b5cf6); color:white; border-radius:8px; width:30px; height:30px; min-width:30px; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:.88rem; }
.algo-text { color:#374151; font-size:.88rem; line-height:1.5; }
.algo-text strong { color:#1e293b; }

.upload-tip { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:.85rem 1.1rem; color:#166534; font-size:.85rem; margin-bottom:.8rem; }
[data-testid="stToolbar"] { display:none !important; }
[data-testid="stDecoration"] { display:none !important; }
header { visibility: hidden !important; }
.footer { text-align:center; color:#94a3b8; font-size:.8rem; margin-top:2.5rem; padding-top:1.5rem; border-top:1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">🎯 Resume Ranking System</div>
    <div class="hero-sub">AI-powered candidate shortlisting using TF-IDF &amp; Cosine Similarity</div>
    <div style="margin-top:10px;position:relative;">
        <span class="hero-badge">TF-IDF</span>
        <span class="hero-badge">Cosine Similarity</span>
        <span class="hero-badge">NLP</span>
        <span class="hero-badge">PDF · DOCX · TXT</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")
    mode = st.radio("Data Source", ["🎬 Demo Mode", "📂 Upload Your Files"], index=0)

    st.markdown("---")
    st.markdown("""
    <div style='background:#f8fafc;border-radius:10px;padding:1rem;font-size:.84rem;color:#374151;'>
    <strong>📎 Supported File Types</strong><br><br>
    📄 &nbsp;<b>PDF</b> — scanned/digital resumes<br>
    📝 &nbsp;<b>DOCX / DOC</b> — Word documents<br>
    📃 &nbsp;<b>TXT</b> — plain text files<br><br>
    <strong>📖 Pipeline</strong><br><br>
    1. Clean &amp; preprocess text<br>
    2. TF-IDF vectorization<br>
    3. Cosine similarity scoring<br>
    4. Rank &amp; export CSV
    </div>
    """, unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────
tab_rank, tab_analysis, tab_algo = st.tabs(["🏆  Rankings", "🔍  Text Analysis", "⚙️  How It Works"])

base_dir   = Path(__file__).parent
sample_jd  = str(base_dir / "job_description.txt")
sample_res = str(base_dir / "resumes")

# ════════════════════════════════════════════════════════
# TAB 1 — RANKINGS
# ════════════════════════════════════════════════════════
with tab_rank:

    jd_path = None
    res_dir = None
    ready   = False

    # ── Demo mode ──────────────────────────────────────
    if "Demo" in mode:
        st.info("ℹ️ **Demo Mode** — 6 sample resumes vs a Python/ML job description. Switch to *Upload Your Files* in sidebar to use your own.", icon="ℹ️")
        jd_path = sample_jd
        res_dir = sample_res
        ready   = True

    # ── Upload mode ────────────────────────────────────
    else:
        st.markdown("""
        <div class="upload-tip">
        ✅ <strong>Accepted formats:</strong> &nbsp;
        <span style='background:#fee2e2;color:#dc2626;border-radius:8px;padding:2px 8px;font-size:.8rem;font-weight:600;'>PDF</span>&nbsp;
        <span style='background:#dbeafe;color:#2563eb;border-radius:8px;padding:2px 8px;font-size:.8rem;font-weight:600;'>DOCX</span>&nbsp;
        <span style='background:#dcfce7;color:#16a34a;border-radius:8px;padding:2px 8px;font-size:.8rem;font-weight:600;'>TXT</span>
        &nbsp; for both Job Description and Resumes.
        </div>
        """, unsafe_allow_html=True)

        col_jd, col_res = st.columns(2)

        with col_jd:
            st.markdown('<div class="sec-hdr">📄 Job Description</div>', unsafe_allow_html=True)
            jd_file = st.file_uploader(
                "Upload job description",
                type=["txt", "pdf", "docx", "doc"],
                key="jd_up",
                label_visibility="collapsed"
            )
            if jd_file:
                ext = Path(jd_file.name).suffix.upper().replace('.','')
                st.success(f"✅ {jd_file.name}  [{ext}]")

        with col_res:
            st.markdown('<div class="sec-hdr">📁 Resume Files</div>', unsafe_allow_html=True)
            res_files = st.file_uploader(
                "Upload resumes (multiple)",
                type=["txt", "pdf", "docx", "doc"],
                accept_multiple_files=True,
                key="res_up",
                label_visibility="collapsed"
            )
            if res_files:
                for rf in res_files:
                    ext = Path(rf.name).suffix.upper().replace('.','')
                    st.write(f"✅ `{rf.name}` [{ext}]")

        ready = bool(jd_file and len(res_files or []) >= 1)
        if not ready and (jd_file or res_files):
            st.warning("⚠️ Upload a job description AND at least 1 resume.")

    # ── Run button ─────────────────────────────────────
    st.markdown("")
    _, btn_col, _ = st.columns([2, 3, 2])
    with btn_col:
        run = st.button("🚀  Rank Candidates", type="primary", use_container_width=True, disabled=not ready)

    # ── Results ────────────────────────────────────────
    if run:
        if "Upload" in mode:
            tmp_dir = tempfile.mkdtemp()
            jd_ext  = Path(jd_file.name).suffix
            jd_path = os.path.join(tmp_dir, f"job_description{jd_ext}")
            with open(jd_path, 'wb') as f:
                f.write(jd_file.read())

            res_dir = os.path.join(tmp_dir, "resumes")
            os.makedirs(res_dir)
            for rf in res_files:
                with open(os.path.join(res_dir, rf.name), 'wb') as f:
                    f.write(rf.read())

        with st.spinner("🔍 Analyzing and ranking candidates..."):
            try:
                df = rank_resumes(jd_path, res_dir, export_csv=False)
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.stop()

        st.markdown("---")

        # Stat cards
        top   = float(df.iloc[0]['Match Score (Raw)']) * 100
        avg   = df['Match Score (Raw)'].mean() * 100
        total = len(df)

        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="stat-card blue"><div class="stat-val">{top:.1f}%</div><div class="stat-lbl">🥇 Top Match Score</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="stat-card green"><div class="stat-val">{avg:.1f}%</div><div class="stat-lbl">📊 Average Score</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="stat-card purple"><div class="stat-val">{total}</div><div class="stat-lbl">👥 Candidates Ranked</div></div>', unsafe_allow_html=True)

        st.markdown("")

        left_col, right_col = st.columns([3, 2])

        medals = {1: ("🥇", "gold"), 2: ("🥈", "silver"), 3: ("🥉", "bronze")}

        with left_col:
            st.markdown('<div class="sec-hdr">🏆 Candidate Rankings</div>', unsafe_allow_html=True)
            for _, row in df.iterrows():
                rank  = int(row['Rank'])
                name  = row['Candidate Name']
                pct_s = row['Match Percentage']
                score = float(row['Match Score (Raw)'])
                ftype = row.get('File Type', 'TXT')
                medal, css = medals.get(rank, (f"#{rank}", ""))

                badge_cls = f"badge-{ftype.lower()}"
                st.markdown(f"""
                <div class="rank-row {css}">
                    <span class="rank-medal">{medal}</span>
                    <span class="rank-name">{name}</span>
                    <span class="rank-badge {badge_cls}">{ftype}</span>
                    <span class="rank-score">{pct_s}</span>
                </div>
                """, unsafe_allow_html=True)
                st.progress(min(score, 1.0))

        with right_col:
            st.markdown('<div class="sec-hdr">📊 Score Chart</div>', unsafe_allow_html=True)
            colors = ["#f59e0b" if i==0 else "#94a3b8" if i==1 else "#d97706" if i==2 else "#3b82f6"
                      for i in range(len(df))]
            fig = go.Figure(go.Bar(
                x=df['Candidate Name'],
                y=df['Match Score (Raw)'] * 100,
                marker_color=colors,
                text=[f"{v:.1f}%" for v in df['Match Score (Raw)'] * 100],
                textposition='outside',
            ))
            fig.update_layout(
                xaxis_title=None, yaxis_title="Match %",
                margin=dict(t=20,b=10,l=10,r=10),
                yaxis=dict(range=[0, max(df['Match Score (Raw)']*100)*1.25]),
                plot_bgcolor='white', paper_bgcolor='white',
                font=dict(family='Inter'), height=320
            )
            st.plotly_chart(fig, use_container_width=True)

            pie_fig = px.pie(
                df, names='Candidate Name',
                values=df['Match Score (Raw)']*100,
                hole=0.45,
                color_discrete_sequence=['#f59e0b','#94a3b8','#d97706','#3b82f6','#10b981','#8b5cf6','#ec4899']
            )
            pie_fig.update_layout(
                margin=dict(t=0,b=0,l=0,r=0),
                showlegend=True,
                legend=dict(font=dict(size=10)),
                height=220
            )
            st.plotly_chart(pie_fig, use_container_width=True)

        # Full table
        st.markdown('<div class="sec-hdr">📋 Full Results Table</div>', unsafe_allow_html=True)
        disp = df[['Rank','Candidate Name','File Type','Match Percentage','Filename']].copy()
        disp.columns = ['Rank','Candidate Name','File Type','Match Score','Source File']
        st.dataframe(disp, use_container_width=True, hide_index=True)

        # CSV download
        st.markdown("")
        csv_data = df[['Rank','Candidate Name','Match Percentage']].to_csv(index=False)
        _, dl, _ = st.columns([2,3,2])
        with dl:
            st.download_button(
                "⬇️  Download Results as CSV",
                data=csv_data,
                file_name="ranking_results.csv",
                mime="text/csv",
                use_container_width=True
            )

# ════════════════════════════════════════════════════════
# TAB 2 — TEXT ANALYSIS
# ════════════════════════════════════════════════════════
with tab_analysis:
    st.markdown('<div class="sec-hdr">🔍 Job Description Keyword Analysis</div>', unsafe_allow_html=True)

    if os.path.exists(sample_jd):
        jd_raw = load_text_file(sample_jd)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**📝 Raw Text**")
            st.text_area("", jd_raw, height=280, key="raw_jd", label_visibility="collapsed")
        with col_b:
            st.markdown("**🧹 After Preprocessing**")
            st.text_area("", preprocess_text(jd_raw), height=280, key="clean_jd", label_visibility="collapsed")

        st.markdown("---")
        st.markdown("**🏷️ Top Keywords (TF-IDF)**")
        kws = extract_keywords(jd_raw, top_n=25)
        st.markdown("".join(f'<span class="chip jd">{k}</span>' for k in kws), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**📊 Top Word Frequencies**")
        cleaned = preprocess_text(jd_raw)
        wf = {}
        for w in cleaned.split():
            wf[w] = wf.get(w, 0) + 1
        freq_df = pd.DataFrame(sorted(wf.items(), key=lambda x:-x[1])[:20], columns=["Word","Frequency"])
        fig2 = px.bar(freq_df, x="Frequency", y="Word", orientation='h',
                      color="Frequency", color_continuous_scale=["#bfdbfe","#3b82f6","#1d4ed8"],
                      text="Frequency")
        fig2.update_layout(yaxis={'categoryorder':'total ascending'},
                           margin=dict(t=10,b=10,l=10,r=10),
                           plot_bgcolor='white', paper_bgcolor='white',
                           coloraxis_showscale=False, height=420)
        st.plotly_chart(fig2, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 3 — HOW IT WORKS
# ════════════════════════════════════════════════════════
with tab_algo:
    st.markdown('<div class="sec-hdr">⚙️ Algorithm Pipeline</div>', unsafe_allow_html=True)

    steps = [
        ("File Parsing",        "Reads .txt, .pdf, and .docx/.doc files automatically. Extracts raw text from each document."),
        ("Text Cleaning",       "Removes URLs, emails, punctuation, and digits from raw text."),
        ("Tokenization",        "Splits cleaned text into individual words using NLTK."),
        ("Stopword Removal",    "Filters out common English words (the, is, a…) that carry no meaning."),
        ("Lemmatization",       "Reduces words to base form: <em>running → run, better → good</em>."),
        ("TF-IDF Vectorization","Converts text into numerical vectors. Captures unigrams and bigrams (2-word phrases)."),
        ("Cosine Similarity",   "Measures the angle between the JD vector and each resume vector. Closer to 1 = better match."),
        ("Ranking & Export",    "Candidates sorted by descending score. Results downloadable as CSV."),
    ]
    for i, (title, desc) in enumerate(steps, 1):
        st.markdown(f"""
        <div class="algo-step">
            <div class="algo-num">{i}</div>
            <div class="algo-text"><strong>{title}</strong><br>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown('<div class="sec-hdr">🧮 Cosine Similarity Formula</div>', unsafe_allow_html=True)
    st.latex(r"\text{Similarity}(A,B)=\frac{A \cdot B}{\|A\|\cdot\|B\|}=\frac{\sum_{i=1}^{n}A_iB_i}{\sqrt{\sum A_i^2}\cdot\sqrt{\sum B_i^2}}")

    st.markdown("")
    st.markdown('<div class="sec-hdr">📦 Tech Stack</div>', unsafe_allow_html=True)
    techs = [("🐍","Python 3.x","Core language"),("📊","scikit-learn","TF-IDF & Cosine Similarity"),
             ("📝","NLTK","NLP preprocessing"),("📄","PyPDF2","PDF text extraction"),
             ("📋","python-docx","Word doc extraction"),("🌐","Streamlit","Web UI")]
    cols = st.columns(len(techs))
    for col, (icon, name, desc) in zip(cols, techs):
        col.markdown(f"""
        <div style='background:white;border-radius:10px;padding:.9rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.07);'>
            <div style='font-size:1.8rem;'>{icon}</div>
            <div style='font-weight:600;font-size:.82rem;color:#1e293b;margin-top:4px;'>{name}</div>
            <div style='font-size:.73rem;color:#64748b;'>{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown('<div class="footer">Resume Ranking System — TF-IDF + Cosine Similarity</div>', unsafe_allow_html=True)
