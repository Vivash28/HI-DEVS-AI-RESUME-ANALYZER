import streamlit as st
import pandas as pd
from pypdf import PdfReader
import docx
import re
from typing import Dict, List, Tuple
from io import StringIO

# ==========================================
# CONFIGURATION
# ==========================================

st.set_page_config(page_title="AI Resume Screener Pro", layout="wide")

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def normalize_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text.lower()).strip()

# ==========================================
# CORE LOGIC
# ==========================================

class ResumeParser:
    """Extracts structured data from resumes."""

    SKILL_DB = [
        "python", "java", "c++", "sql", "aws", "docker", "kubernetes",
        "react", "angular", "django", "flask", "machine learning",
        "data analysis", "communication", "project management",
        "git", "linux", "html", "css", "javascript",
        "typescript", "node.js", "pandas", "numpy"
    ]

    @staticmethod
    def extract_text(uploaded_file) -> str:
        text = ""
        try:
            if uploaded_file.name.endswith(".pdf"):
                pdf = PdfReader(uploaded_file)
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"

            elif uploaded_file.name.endswith(".docx"):
                doc = docx.Document(uploaded_file)
                for para in doc.paragraphs:
                    text += para.text + "\n"

            elif uploaded_file.name.endswith(".txt"):
                text = uploaded_file.read().decode("utf-8")

        except Exception as e:
            st.error(f"Error reading {uploaded_file.name}: {e}")

        return text

    @staticmethod
    def extract_email(text: str) -> str:
        match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        return match.group(0) if match else "Not Found"

    @staticmethod
    def extract_phone(text: str) -> str:
        match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        return match.group(0) if match else "Not Found"

    @staticmethod
    def extract_name(text: str) -> str:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if lines:
            # Usually first non-empty line is name
            if len(lines[0].split()) <= 4:
                return lines[0]
        return "Unknown"

    @staticmethod
    def extract_skills(text: str) -> List[str]:
        text_lower = normalize_text(text)
        found = []
        for skill in ResumeParser.SKILL_DB:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found.append(skill)
        return list(set(found))

    @staticmethod
    def extract_experience(text: str) -> int:
        text_lower = normalize_text(text)

        # Match patterns like: 3 years, 5+ years
        matches = re.findall(r'(\d+)\+?\s*years?', text_lower)
        if matches:
            return max(map(int, matches))

        # Match experience ranges like: 2018 - 2023
        years = re.findall(r'(20\d{2})', text_lower)
        if len(years) >= 2:
            try:
                return max(map(int, years)) - min(map(int, years))
            except:
                return 0

        return 0

    @staticmethod
    def parse(text: str) -> Dict:
        return {
            "name": ResumeParser.extract_name(text),
            "email": ResumeParser.extract_email(text),
            "phone": ResumeParser.extract_phone(text),
            "skills": ResumeParser.extract_skills(text),
            "years_experience": ResumeParser.extract_experience(text),
            "raw_text": text
        }


class JobMatcher:
    def __init__(self, required_skills: List[str], min_exp: int):
        self.req_skills = set(normalize_text(s) for s in required_skills)
        self.min_exp = min_exp

    def calculate_score(self, candidate: Dict) -> Tuple[float, List[str], float]:
        candidate_skills = set(candidate["skills"])
        candidate_exp = candidate["years_experience"]

        if not self.req_skills:
            skill_score = 100
            missing = []
        else:
            matched = candidate_skills.intersection(self.req_skills)
            missing = list(self.req_skills - candidate_skills)
            skill_score = (len(matched) / len(self.req_skills)) * 100

        # Experience score
        if candidate_exp >= self.min_exp:
            exp_score = 100
        else:
            exp_score = (candidate_exp / self.min_exp) * 100 if self.min_exp > 0 else 100

        final_score = (skill_score * 0.7) + (exp_score * 0.3)

        return round(final_score, 1), missing, round(skill_score, 1)


# ==========================================
# SIDEBAR CONFIG
# ==========================================

with st.sidebar:
    st.header("⚙️ Job Configuration")

    job_title = st.text_input("Job Title", "Senior Python Developer")
    min_exp = st.slider("Minimum Experience (Years)", 0, 15, 3)

    req_skills_input = st.text_area(
        "Required Skills (comma separated)",
        "Python, SQL, AWS, Django, Docker"
    )

    req_skills = [s.strip().lower() for s in req_skills_input.split(",") if s.strip()]

    st.divider()
    st.info(f"Tracking {len(req_skills)} required skills")


# ==========================================
# MAIN UI
# ==========================================

st.title("📄 AI Resume Analyzer Pro")
st.markdown("Upload resumes to automatically parse, rank, and analyze candidates.")

uploaded_files = st.file_uploader(
    "Upload Resumes (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

if uploaded_files:

    matcher = JobMatcher(req_skills, min_exp)
    results = []

    progress = st.progress(0)

    for i, file in enumerate(uploaded_files):

        text = ResumeParser.extract_text(file)
        candidate = ResumeParser.parse(text)
        score, missing, skill_percent = matcher.calculate_score(candidate)

        recommendation = "Reject"
        if score >= 85:
            recommendation = "Strong Hire"
        elif score >= 60:
            recommendation = "Interview"

        results.append({
            "Name": candidate["name"],
            "Score": score,
            "Skill Match %": skill_percent,
            "Experience": candidate["years_experience"],
            "Recommendation": recommendation,
            "Email": candidate["email"],
            "Missing Skills": ", ".join(missing),
            "Matched Skills": ", ".join(candidate["skills"])
        })

        progress.progress((i + 1) / len(uploaded_files))

    df = pd.DataFrame(results).sort_values(by="Score", ascending=False)

    # ==========================================
    # ANALYTICS DASHBOARD
    # ==========================================

    st.subheader("📊 Summary Analytics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Candidates", len(df))

    with col2:
        strong = len(df[df["Recommendation"] == "Strong Hire"])
        st.metric("Strong Hires", strong)

    with col3:
        avg_score = round(df["Score"].mean(), 1)
        st.metric("Average Score", avg_score)

    st.divider()

    # ==========================================
    # TABLE VIEW
    # ==========================================

    st.subheader("📋 Ranked Candidates")

    st.dataframe(
        df[["Name", "Score", "Skill Match %", "Experience", "Recommendation", "Email"]],
        use_container_width=True,
        hide_index=True
    )

    # Download button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download Results as CSV",
        csv,
        "resume_screening_results.csv",
        "text/csv"
    )

    # ==========================================
    # DETAILED VIEW
    # ==========================================

    st.subheader("🔍 Candidate Details")

    for _, row in df.iterrows():
        with st.expander(f"{row['Name']} - {row['Score']}% ({row['Recommendation']})"):

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Email:**", row["Email"])
                st.write("**Experience:**", f"{row['Experience']} Years")
                st.write("**Recommendation:**", row["Recommendation"])

            with col2:
                st.write("**Matched Skills:**")
                st.success(row["Matched Skills"] or "None")

                st.write("**Missing Skills:**")
                if row["Missing Skills"]:
                    st.error(row["Missing Skills"])
                else:
                    st.success("All Required Skills Matched 🎯")

else:
    st.info("👋 Upload resumes to start screening.")
