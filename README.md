An intelligent resume screening web application built with Streamlit that automatically parses resumes (PDF, DOCX, TXT), extracts candidate information, matches skills against job requirements, and ranks candidates with a smart scoring system.

Features

Upload multiple resumes at once (PDF, DOCX, TXT)

Automatic extraction of:

Name

Email

Phone number

Skills

Years of experience

Skill-based job matching system

Weighted scoring algorithm (Skills 70% + Experience 30%)

Automatic candidate ranking

Summary analytics dashboard

Download results as CSV

Detailed candidate breakdown view

Tech Stack

Python 3.8+

Streamlit

Pandas

pypdf

python-docx

Regex (for parsing logic)

Installation
Clone the Repository
git clone https://github.com/your-username/ai-resume-analyzer.git
cd ai-resume-analyzer

Create Virtual Environment (Recommended)
python -m venv venv
venv\Scripts\activate   # Windows
# OR
source venv/bin/activate  # Mac/Linux

Install Dependencies
pip install -r requirements.txt


Or manually:

pip install streamlit pandas pypdf python-docx

Running the Application
streamlit run main.py


The app will open automatically in your browser at:

http://localhost:8501

 How It Works
Job Configuration (Sidebar)

Enter job title

Set minimum years of experience

Define required skills (comma-separated)

Resume Upload

Upload multiple resumes in:

PDF

DOCX

TXT

AI Parsing & Scoring

The system:

Extracts text from resumes

Identifies key details

Matches skills

Calculates score using:

Final Score = (Skill Match × 70%) + (Experience Match × 30%)

Results Dashboard

You get:

Ranked candidates table

Strong Hire / Interview / Reject recommendation

Skill match percentage

CSV export option

Scoring Logic
Component	Weight
Skills Match	70%
Experience Match	30%
Recommendation Rules

Strong Hire → Score ≥ 85%

Interview → Score ≥ 60%

Reject → Score < 60%

Project Structure
AI-Resume-Analyzer/
│
├── main.py
├── README.md
├── requirements.txt
└── sample_resumes/

Future Improvements

GPT-powered resume understanding

Skill frequency visualizations

Auto Top-5 shortlist

Email draft generator for recruiters

Cloud deployment (Streamlit Cloud / AWS)

 Limitations

Skill detection is keyword-based

Experience extraction is pattern-based (not AI inferred)

Resume formatting may affect text extraction quality
