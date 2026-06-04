# git pull origin main --rebase
# git push origin main
# echo ".streamlit/secrets.toml" >> .gitignore
# git add .
# git commit -m "removed secrets"
# git push

import uuid
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import jwt
import datetime
import re
from difflib import get_close_matches
import os
import PyPDF2

# communication and interview libraries
from audiorecorder import audiorecorder
import speech_recognition as sr
from textblob import TextBlob
import time
import cv2

pd.options.mode.copy_on_write = True
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["OPENBLAS_NUM_THREADS"] = "2"


# ==========================
# SESSION INITIALIZATION
# ==========================

if "role" not in st.session_state:
    st.session_state["role"] = None

if "username" not in st.session_state:
    st.session_state["username"] = None

if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None

st.set_page_config(
    page_title="Placement Intelligence Apex",
    layout="wide",
    page_icon="  "
)


# ================================
# CUSTOM CSS FOR LOGIN PAGE
# ================================

st.markdown("""
<style>

/* Main background */
.stApp {
    background: linear-gradient(135deg,#0f172a,#020617);
    color:white;
}

/* Glass card style */
.glass-card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.15);
    padding: 25px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
}

/* Glass header */
.glass-header {
    background: rgba(139,92,246,0.35);
    backdrop-filter: blur(15px);
    border-radius: 14px;
    padding: 20px;
    text-align:center;
    font-size:28px;
    font-weight:bold;
    color:white;
}

/* KPI glass cards */
.metric-card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    padding: 15px;
    border:1px solid rgba(255,255,255,0.12);
}

/* Input glass */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.08);
    color:white;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)



import google.generativeai as genai
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")

def call_gemini(prompt):

    try:
        response = model.generate_content(prompt)
        return response.text


    except Exception as e:
        return f"Error: {str(e)}"


# ================================
# SESSION INIT
# ================================

if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None

# ================================
# SECRET KEY
# ================================
SECRET_KEY = st.secrets.get("SECRET_KEY", "fallback_secret_2026")


# ================================
# OFFICIAL USERS
# ================================

OFFICIAL_USERS = {
    "placement_officer": {"password": "official123", "role": "Official"},
    "coordinator": {"password": "official123", "role": "Official"},
    "naash": {"password": "naash123", "role": "Official"},
    "vellai_pandhu": {"password": "kusu123", "role": "Official"}
}

# ================================
# COMPANY ADMINS
# ================================

COMPANY_ADMINS = {
    "tcs_admin": {"password": "tcs123", "company": "TCS", "role": "Admin"},
    "infosys_admin": {"password": "infosys123", "company": "Infosys", "role": "Admin"},
}

# ================================
# JWT TOKEN
# ================================

def create_token(payload):

    payload["exp"] = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=8)

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token


def verify_token(token):

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded

    except:
        return None


# ================================
# LOGIN PAGE
# ================================

def login_page():

    col1,col2,col3 = st.columns([1,2,1])

    with col2:

  

        login_type = st.selectbox(
            "Login As",
            [
                "Official (Placement Cell)",
                "Student",
                "Company Admin"
            ]
        )

        username = st.text_input("Username / StudentID")

        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):

            # =============================
            # OFFICIAL LOGIN
            # =============================

            if login_type == "Official (Placement Cell)":

                if username in OFFICIAL_USERS and password == OFFICIAL_USERS[username]["password"]:

                    token = create_token({
                        "role": "Official",
                        "username": username
                    })

                    st.session_state["auth_token"] = token
                    st.session_state["role"] = "Official"
                    st.session_state["username"] = username

                    st.success("Official Login Successful")
                    st.rerun()

                else:
                    st.error("Invalid Official Credentials")

            # =============================
            # STUDENT LOGIN
            # =============================

            elif login_type == "Student":

                if password == "student":

                    token = create_token({
                        "role": "Student",
                        "student_id": username
                    })

                    st.session_state["auth_token"] = token
                    st.session_state["role"] = "Student"
                    st.session_state["student_id"] = username

                    st.success("Student Login Successful")
                    st.rerun()

                else:
                    st.error("Invalid Student Password")

            # =============================
            # COMPANY ADMIN LOGIN
            # =============================

            elif login_type == "Company Admin":

                if username in COMPANY_ADMINS and password == COMPANY_ADMINS[username]["password"]:

                    token = create_token({
                        "role": "Admin",
                        "username": username,
                        "company": COMPANY_ADMINS[username]["company"]
                    })

                    st.session_state["auth_token"] = token
                    st.session_state["role"] = "Admin"
                    st.session_state["company"] = COMPANY_ADMINS[username]["company"]
                    st.session_state["username"] = username

                    st.success("Company Admin Login Successful")
                    st.rerun()

                else:
                    st.error("Invalid Company Admin Credentials")

        st.markdown('</div>', unsafe_allow_html=True)


# ================================
# AUTH CHECK
# ================================

if st.session_state["auth_token"] is None:
    login_page()
    st.stop()

user = verify_token(st.session_state["auth_token"])

if user is None:
    st.error("Session expired. Please login again.")
    st.session_state["auth_token"] = None
    st.rerun()
role = user["role"]

st.write("Logged Role:", role)

# GET ROLE FROM TOKEN
role = user["role"]
username = user.get("username", "")
student_id = user.get("student_id", "")
company = user.get("company", "")

@st.cache_data(show_spinner=False)
def load_and_prepare_data():

    # ================= LOAD FILES =================
    df_master = pd.read_csv("placement_master_10yr_full_dataset.csv", low_memory=False)
    academics = pd.read_csv("academic_history_10years.csv", low_memory=False)
    placements = pd.read_csv("placement_history_10years.csv", low_memory=False)
    companies = pd.read_csv("companies_master.csv", low_memory=False)
    drives = pd.read_csv("mis_drives_10years.csv", low_memory=False)
    

    # ================= CLEAN COLUMNS =================
    df_master.columns = df_master.columns.str.strip()
    academics.columns = academics.columns.str.strip()
    placements.columns = placements.columns.str.strip()

    # ================= MERGE =================
    df = df_master.merge(placements, on="StudentID", how="left")
    df = df.merge(academics, on="StudentID", how="left")

    # ================= AUTO GENERATE DATA =================
    for i in range(1, 9):

        if f"SGPA_Sem{i}" not in df.columns:
            df[f"SGPA_Sem{i}"] = np.random.uniform(6.5, 9.5, len(df)).round(2)

        if f"Backlogs_Sem{i}" not in df.columns:
            df[f"Backlogs_Sem{i}"] = np.random.randint(0, 2, len(df))

        if f"Attendance_Sem{i}" not in df.columns:
            df[f"Attendance_Sem{i}"] = np.random.uniform(70, 95, len(df)).round(1)

    subjects = ["Maths", "DSA", "OS", "DBMS", "AI"]

    for s in subjects:
        for sem in range(1, 9):
            col = f"{s}_Sem{sem}"
            if col not in df.columns:
                df[col] = np.random.randint(55, 100, len(df))

    return df, companies, drives
df, companies, drives = load_and_prepare_data()

@st.cache_data(show_spinner=False)
def preprocess_all(df):

    placed_df = df[df["Status"] == "Placed"].copy()

    # KPIs
    total_students = df["StudentID"].nunique()
    placed_students = placed_df["StudentID"].nunique()
    companies = df["Company"].nunique()
    avg_package = round(placed_df["Package"].mean(), 2)
    placement_rate = round((placed_students / total_students) * 100, 2)

    # Charts
    trend_df = df.groupby("Year")["StudentID"].count().reset_index()
    branch_df = placed_df.groupby("Branch")["StudentID"].count()

    # Light version for charts
    sample_df = df.sample(min(len(df), 3000))

    return {
        "placed_df": placed_df,
        "kpi": (total_students, placed_students, companies, avg_package, placement_rate),
        "trend": trend_df,
        "branch": branch_df,
        "sample": sample_df
    }


cache = preprocess_all(df)
placed_df = cache["placed_df"]
total_students, placed_students, companies, avg_package, placement_rate = cache["kpi"]
trend_df = cache["trend"]
branch_df = cache["branch"]
sample_df = cache["sample"]

# ==============================
# COLUMN STABILIZER
# ==============================

required_cols = {
    "StudentID": "Unknown",
    "Name": "Unknown",
    "Branch": "Unknown",
    "Company": "Not Applied",
    "Status": "Not Placed",
    "Package": 0,
    "Year": 2026,
    "Skills": "Python,SQL"
}

for col, default in required_cols.items():
    if col not in df.columns:
        df[col] = default

# Convert date column if present
if "Placed_Date" in df.columns:
    df["Placed_Date"] = pd.to_datetime(df["Placed_Date"], errors="coerce")


# ==========================================================
# AI NARRATIVE INTERPRETATION ENGINE
# ==========================================================

def generate_narrative_report(df):

    placed = df[df["Status"] == "Placed"].copy()

    report = {}

    # ---------------- Hiring Performance ----------------
    company_hires = placed["Company"].value_counts()
    top_company = company_hires.idxmax() if not company_hires.empty else "N/A"
    top_count = company_hires.max() if not company_hires.empty else 0
    

    report["Hiring Performance"] = (
        f"{top_company} recruited the highest number of students "
        f"with {top_count} successful hires, indicating strong "
        f"recruitment activity from this company."
    )

    # ---------------- Package Analysis ----------------
    avg_package = placed.groupby("Company")["Package"].mean()

    highest_company = avg_package.idxmax()
    highest_package = avg_package.max()

    median_salary = placed["Package"].median()

    report["Package Analysis"] = (
        f"{highest_company} offers the highest average package "
        f"at   {round(highest_package,2)} LPA. "
        f"The median package across companies is about "
        f"  {round(median_salary,2)} LPA."
    )

    # ---------------- Branch Analysis ----------------
    branch_hires = placed["Branch"].value_counts()
    top_branch = branch_hires.idxmax()

    report["Branch Performance"] = (
        f"The {top_branch} branch shows the strongest placement "
        f"performance with the highest number of successful placements."
    )

    # ---------------- Placement Rate ----------------
    total_students = df["StudentID"].nunique()
    placed_students = placed["StudentID"].nunique()

    placement_rate = (placed_students / total_students) * 100

    report["Placement Rate"] = (
        f"The university placement rate is {round(placement_rate,2)}%, "
        f"with {placed_students} students placed out of {total_students}."
    )

    # ---------------- Company Difficulty ----------------
    applicants = df.groupby("Company")["StudentID"].count()
    selected = placed.groupby("Company")["StudentID"].count()

    difficulty = (applicants / selected).replace(np.inf,0)
    hardest_company = difficulty.idxmax()

    report["Company Difficulty"] = (
        f"{hardest_company} appears to be the most competitive company "
        f"based on the applicant-to-selection ratio."
    )

    # ---------------- Skill Demand ----------------
    skills = df["Skills"].str.split(",", expand=True).stack().value_counts()
    top_skill = skills.idxmax()

    report["Skill Demand"] = (
        f"The most demanded skill among placed students is {top_skill}."
    )

    # ---------------- Placement Trend ----------------
    yearly = placed.groupby("Year")["StudentID"].nunique()
    best_year = yearly.idxmax()

    report["Placement Trend"] = (
        f"The strongest placement performance occurred in {best_year}."
    )

    return report


# ==========================================================
# RULE-BASED AI COPILOT
# ==========================================================

def placement_ai_copilot(question, df):

    placed = df[df["Status"]=="Placed"]
    question = question.lower()

    if "highest package" in question or "top paying" in question:

        avg_package = placed.groupby("Company")["Package"].mean()
        company = avg_package.idxmax()
        package = avg_package.max()

        return f"The highest paying company is {company} offering about   {round(package,2)} LPA."

    elif "most students" in question or "most hiring" in question:

        hires = placed["Company"].value_counts()
        company = hires.idxmax()
        count = hires.max()

        return f"{company} hired the highest number of students ({count})."

    elif "placement rate" in question:

        total = df["StudentID"].nunique()
        placed_students = placed["StudentID"].nunique()

        rate = (placed_students/total)*100

        return f"The placement rate is {round(rate,2)}%."

    elif "best branch" in question:

        branch = placed["Branch"].value_counts().idxmax()

        return f"The branch with the highest placements is {branch}."

    elif "skills" in question:

        skills = df["Skills"].str.split(",",expand=True).stack().value_counts()
        top_skill = skills.idxmax()

        return f"The most demanded skill is {top_skill}."

    else:
        return "Try asking about companies, packages, branches, skills, or placement rate."


# ============================================================
# COLUMN INTELLIGENCE ENGINE
# ============================================================

def detect_columns(question, df):

    q = question.lower()
    columns = list(df.columns)

    detected = []

    for col in columns:

        name = col.lower().replace("_"," ")

        if name in q:
            detected.append(col)

        else:

            words = name.split()

            for w in words:

                if w in q:
                    detected.append(col)

    # fuzzy matching
    for word in q.split():

        match = get_close_matches(word, columns, n=1, cutoff=0.8)

        if match:
            detected.append(match[0])

    return list(set(detected))


# ============================================================
# YEAR DETECTION
# ============================================================

def detect_year(question):

    year_match = re.search(r"\b20\d{2}\b", question)

    if year_match:
        return int(year_match.group())

    return None


# ============================================================
#  GPT POWERED AI ENGINE (ULTIMATE VERSION)
# ============================================================

def gpt_ai_engine(question, df):

    sample = df.head(100)

    prompt = f"""
You are a data analyst AI.

Dataset sample:
{sample}

User question:
{question}

Give clear insights.
"""

    try:
        response = model.generate_content(prompt)
        return response.text
        return getattr(response, "text", "No response generated")

    except Exception as e:
        return f"Error: {str(e)}"
# ==========================================================
# PLACEMENT SCORE
# ==========================================================

def placement_score(profile):

    sgpa = np.mean([profile[f"SGPA_Sem{i}"] for i in range(1, 9)])
    backlogs = sum([profile[f"Backlogs_Sem{i}"] for i in range(1, 9)])
    skills = len(str(profile.get("Skills", "")).split(","))
    attendance = np.mean([profile[f"Attendance_Sem{i}"] for i in range(1, 9)])

    score = (
        sgpa * 10 * 0.4 +
        (skills * 5) * 0.2 +
        attendance * 0.2 -
        backlogs * 5
    )

    return max(0, min(100, round(score, 2)))


# ==========================================================
# AI SUMMARY
# ==========================================================

def ai_summary(profile):

    sgpa = np.mean([profile[f"SGPA_Sem{i}"] for i in range(1, 9)])
    backlogs = sum([profile[f"Backlogs_Sem{i}"] for i in range(1, 9)])
    skills = len(str(profile.get("Skills", "")).split(","))

    if sgpa > 8 and backlogs == 0:
        return "Excellent academic performance. Strong placement potential."

    elif sgpa > 7:
        return "Good academic record. Improve skills to increase placement chances."

    elif backlogs > 2:
        return "Backlogs are affecting placement chances. Focus on clearing them."

    else:
        return "Moderate performance. Needs improvement in academics and skills."


# ==========================================================
# ML MODEL TRAINING
# ==========================================================

from sklearn.ensemble import RandomForestClassifier

@st.cache_resource
def train_model_cached(df):
    model_df = df.copy()


    model_df["Placed_Flag"] = (model_df["Status"] == "Placed").astype(int)

    model_df["Avg_SGPA"] = model_df[[f"SGPA_Sem{i}" for i in range(1,9)]].mean(axis=1)
    model_df["Total_Backlogs"] = model_df[[f"Backlogs_Sem{i}" for i in range(1,9)]].sum(axis=1)
    model_df["Avg_Attendance"] = model_df[[f"Attendance_Sem{i}" for i in range(1,9)]].mean(axis=1)
    model_df["Skill_Count"] = model_df["Skills"].apply(lambda x: len(str(x).split(",")))

    X = model_df[["Avg_SGPA","Total_Backlogs","Avg_Attendance","Skill_Count"]]
    y = model_df["Placed_Flag"]

    rf_model = RandomForestClassifier(n_estimators=30, max_depth=8)
    rf_model.fit(X, y)
    return rf_model

# Load model once
ml_model = train_model_cached(df)


# ==========================================================
# STUDENT RANKING
# ==========================================================

def rank_students(df, model):

    temp = df.copy()

    temp["Avg_SGPA"] = temp[[f"SGPA_Sem{i}" for i in range(1, 9)]].mean(axis=1)
    temp["Total_Backlogs"] = temp[[f"Backlogs_Sem{i}" for i in range(1, 9)]].sum(axis=1)
    temp["Avg_Attendance"] = temp[[f"Attendance_Sem{i}" for i in range(1, 9)]].mean(axis=1)
    temp["Skill_Count"] = temp["Skills"].apply(lambda x: len(str(x).split(",")))

    X = temp[["Avg_SGPA", "Total_Backlogs", "Avg_Attendance", "Skill_Count"]]

    temp["Score"] = model.predict_proba(X)[:, 1]
    temp["Rank"] = temp["Score"].rank(ascending=False)

    return temp


# ==========================================================
# GRAPH INTERPRETER
# ==========================================================

def interpret_graph(title, data):

    if title == "SGPA":
        avg = data["SGPA"].mean()
        trend = "improving" if data["SGPA"].iloc[-1] > data["SGPA"].iloc[0] else "declining"
        return f"The student's academic performance is {trend} with an average SGPA of {round(avg, 2)}."

    elif title == "Backlogs":
        total = data["Backlogs"].sum()
        return f"The student has {total} total backlogs across semesters."

    elif title == "Attendance":
        avg = data["Attendance"].mean()
        status = "good" if avg > 75 else "poor"
        return f"Average attendance is {round(avg, 1)}%, indicating {status} consistency."

    elif title == "Subjects":
        top = data.sort_values("Marks", ascending=False).iloc[0]["Subject"]
        return f"The strongest subject appears to be {top}."

    elif title == "Placement":
        offers = len(data[data["Status"] == "Placed"])
        attempts = len(data)
        rate = round((offers / attempts) * 100, 2) if attempts > 0 else 0
        return f"The student has a placement success rate of {rate}%."

    return "No interpretation available."

# ==========================================================
# AI INTERVIEW QUESTION GENERATOR
# ==========================================================

def generate_question(topic, level):
    prompt = f"""
You are an expert technical interviewer.

Ask ONE {level} level interview question for:
{topic}

Make it:
- Industry relevant
- Asked in real interviews
- Not generic

Only give question.
"""
    return call_gemini(prompt)
# ==========================================================
#camera face detection for attendance
import cv2

def detect_faces(frame):

    @st.cache_resource
    def load_cascade():
        return cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    face_cascade = load_cascade()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    return len(faces)

#=========================================================
# fraud check based on face count
#==========================================================

def fraud_check(face_count):

    if face_count == 0:
        return "No face detected"

    elif face_count > 1:
        return "Multiple persons detected"

    return "OK"

# ==========================================================
# AI ANSWER EVALUATOR
# ==========================================================
def evaluate_answer(question, answer):

    prompt = f"""
Question: {question}
Answer: {answer}

Evaluate:
- Score /10
- Feedback
"""

    response = model.generate_content(prompt)
    return response.text
    return getattr(response, "text", "No response generated")

# ==========================================================
# SPEECH TO TEXT
# ==========================================================
def speech_to_text(audio_bytes):
    recognizer = sr.Recognizer()
    text = recognizer.recognize_google(audio_data, language="en-IN")

    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        filename = f.name

    try:
        with sr.AudioFile(filename) as source:
            audio = recognizer.record(source)

        return recognizer.recognize_google(audio)

    except:
        return ""
    

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Home"
# ==========================================================
# HEADER STYLE
# ==========================================================

st.markdown("""
<style>

/* ===== MAIN BACKGROUND ===== */
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a);
    color: #e2e8f0;
}

/* ===== REMOVE HEADER SPACE ===== */
header {visibility: hidden;}
.block-container {padding-top: 1rem;}

/* ===== GLASS HEADER ===== */
.glass-header {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    padding: 20px;
    border-radius: 14px;
    font-size: 26px;
    font-weight: 700;
    color: white;
    box-shadow: 0 10px 40px rgba(0,0,0,0.4);
}

/* ===== CARD ===== */
.card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(18px);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}

/* ===== KPI ===== */
.kpi-card {
    background: rgba(255,255,255,0.05);
    padding: 18px;
    border-radius: 14px;
    text-align: center;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    transition: 0.3s;
}
.kpi-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(99,102,241,0.4);
}

.kpi-title {
    font-size: 14px;
    color: #cbd5f5;
}
.kpi-value {
    font-size: 26px;
    font-weight: bold;
    color: white;
}
.kpi-delta {
    font-size: 13px;
    color: #22c55e;
}

/* ===== INPUT ===== */
.stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    color: white !important;
    border-radius: 10px;
}

/* ===== BUTTON ===== */
.stButton button {
    background: linear-gradient(90deg,#6366f1,#8b5cf6);
    color: white;
    border-radius: 10px;
    border: none;
}
.stButton button:hover {
    opacity: 0.85;
}

/* ===== TABS ===== */
button[data-baseweb="tab"] {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
}
button[aria-selected="true"] {
    background: linear-gradient(90deg,#6366f1,#8b5cf6);
    color: white;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #6366f1;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


st.markdown(
    '<div class="purple-header"> drift project </div>',
    unsafe_allow_html=True
)


# ==========================================================
# ROLE BASED TABS
# ==========================================================

if role == "Official":
    tabs = [
        "Home",
        "University Dashboard",
        "Student Dashboard",
        "Admin Company Analysis",
        "Company Dashboard",
        "New Company Drive",
        "Communication Analyzer",
        "Mock Interview"
    ]

elif role == "Admin":
    tabs = [
        "Home",
        "Company Dashboard",
        "New Company Drive"
    ]

elif role == "Student":
    tabs = [
        "Home",
        "Student Dashboard",
        "Mock Interview"
    ]


if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = tabs[0]


cols = st.columns(len(tabs))

for i, tab in enumerate(tabs):
    if cols[i].button(
        tab,
        use_container_width=True,
        type="primary" if st.session_state["active_tab"] == tab else "secondary"
    ):
        st.session_state["active_tab"] = tab


selected_tab = st.session_state["active_tab"]

if selected_tab == "Home":

    import datetime

    username = st.session_state.get("username", "User")

    # ================= HEADER =================
    col1, col2 = st.columns([8,1])

    with col1:
        st.markdown("""
        <div class="glass-header">
            Placement Intelligence Apex
        </div>
        """, unsafe_allow_html=True)
        st.write(f"Welcome **{username}**")

    with col2:
        if st.button("Logout"):
            st.session_state["auth_token"] = None
            st.session_state["role"] = None
            st.session_state["username"] = None
            st.rerun()

    now = datetime.datetime.now()
    st.caption(now.strftime("%A | %d %B %Y | %H:%M:%S"))

    st.markdown("---")

    # ================= DATA =================
    total_students = df["StudentID"].nunique()
    placed_students = df[df["Status"]=="Placed"]["StudentID"].nunique()
    companies = df["Company"].nunique()
    avg_package = round(df[df["Status"]=="Placed"]["Package"].mean(),2)
    placement_rate = round((placed_students/total_students)*100,2)

    # ================= FAKE TREND (you can replace with real) =================
    import random
    t1 = f"+{random.randint(2,10)}%"
    t2 = f"+{random.randint(2,10)}%"
    t3 = f"+{random.randint(1,5)}%"
    t4 = f"+{random.randint(1,5)}%"
    t5 = f"+{random.randint(2,8)}%"

    # ================= KPI CARDS =================
    c1,c2,c3,c4 = st.columns(4)

    def kpi(title, value, delta):
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-delta">{delta}</div>
        </div>
        """, unsafe_allow_html=True)

    with c1:
        kpi("Total Students", f"{total_students} / {placed_students}", t1) 

    with c2:
        kpi("Companies", companies, t2)

    with c3:
        kpi("Avg Package (LPA)", avg_package, t3)

    with c4:
        kpi("Placement Rate", f"{placement_rate}%", t4)

    st.markdown("----")

    # ================= SECOND ROW (INSIGHTS PANEL) =================
    colA, colB = st.columns([2,1])

    with colA:
        st.markdown("### Placement Trend")
        fig_trend = px.line(trend_df, x="Year", y="StudentID", markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)

    with colB:
        st.markdown("### Quick Insights")
        st.info(f"""
         Placement Rate is {placement_rate}%  
         Average Package is {avg_package} LPA  
         {companies} companies participated  
        """)

    c6 = st.columns(1)

    with c6:
        st.markdown("### Branch-wise Placement")
        branch_df_reset = branch_df.reset_index()

        fig_branch = px.bar(
            branch_df_reset,
            x="Branch",
            y="StudentID",
            title="Branch-wise Placement"
        )

        st.plotly_chart(fig_branch, use_container_width=True)

   
    # =======================
    # AI DATASET ANALYST
    # =======================
    st.subheader("AI Dataset Analyst")

    query = st.text_input("Ask anything about the dataset")

    if st.button("Analyze"):

        if not query:
            st.warning("Enter a question")
        else:
            with st.spinner("Analyzing..."):

                prompt = f"""
    You are a STRICT data analyst.

    Dataset columns:
    {list(df.columns)}

    Sample:
    {df.head(5).to_string()}

    User question:
    {query}

    Rules:
    - Only use given columns
    - Give short bullet insights
    - No assumptions
    """

                result = call_gemini(prompt)
                st.success(result)
    # =======================
    # AI GRAPH GENERATOR
    # =======================
    st.subheader("Graph Generator")

    graph_query = st.text_input("Ask for any graph")

    if st.button("Generate Graph"):

        if not graph_query:
            st.warning("Enter graph request")

        else:
            with st.spinner("Generating..."):

                prompt = f"""
    You are a STRICT data visualization AI.

    Columns:
    {list(df.columns)}

    User request:
    {graph_query}

    Return EXACTLY in this format:
    chart|x_column|y_column

    Example:
    bar|Company|Package

    ONLY RETURN THIS FORMAT.
    """

                result = call_gemini(prompt)

                try:
                    chart, x_col, y_col = result.strip().split("|")

                    chart = chart.lower()

                    if x_col not in df.columns or y_col not in df.columns:
                        st.error("Invalid columns from AI")
                    else:

                        if chart == "bar":
                            fig = px.bar(df, x=x_col, y=y_col)

                        elif chart == "line":
                            fig = px.line(df, x=x_col, y=y_col)

                        elif chart == "pie":
                            fig = px.pie(df, names=x_col, values=y_col)

                        elif chart == "scatter":
                            fig = px.scatter(df, x=x_col, y=y_col)

                        else:
                            st.error("Unsupported chart type")
                            fig = None

                        if fig:
                            st.plotly_chart(fig, use_container_width=True)

                            #  AI explanation
                            explanation = call_gemini(f"""
    Explain insights:

    X: {x_col}
    Y: {y_col}

    Give trends and meaning.
    """)
                            st.info(explanation)

                except:
                    st.error("AI failed. Try simpler query like 'package vs company'")
# =======================
# UNIVERSITY DASHBOARD
# =======================
if selected_tab == "University Dashboard":
    st.markdown("##    Placement Overview Dashboard")

    # ---------------- YEAR-WISE PLACEMENT RATE ----------------
    st.markdown("###    Year-wise Placement Rate")

    year_placement = df.groupby("Year").apply(
        lambda x: round((x[x["Status"]=="Placed"]["StudentID"].nunique()
                         / x["StudentID"].nunique())*100,2)
    ).reset_index()

    year_placement.columns = ["Year", "Placement Rate (%)"]

    fig2 = px.line(
        year_placement,
        x="Year",
        y="Placement Rate (%)",
        markers=True
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ---------------- YEAR-WISE AVERAGE PACKAGE ----------------
    st.markdown("###    Year-wise Average Package")

    year_package = df[df["Status"]=="Placed"].groupby("Year")["Package"].mean().reset_index()
    year_package["Package"] = round(year_package["Package"],2)

    fig3 = px.area(
        year_package,
        x="Year",
        y="Package"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ---------------- STATUS DISTRIBUTION ----------------
    st.markdown("###    Overall Placement Distribution")

    status_count = df["Status"].value_counts().reset_index()
    status_count.columns = ["Status", "Count"]

    fig4 = px.pie(
        status_count,
        names="Status",
        values="Count",
        hole=0.5
    )
    st.plotly_chart(fig4, use_container_width=True)


    #-----------------Year-wise Placement Performance
    st.subheader("Year-wise Placement Performance")
    yearly = df[df["Status"]=="Placed"].groupby("Year")["StudentID"].nunique().reset_index()
    fig1 = px.bar(yearly, x="Year", y="StudentID", template="plotly_white",
                  title="Year-wise Unique Placements")
    st.plotly_chart(fig1, use_container_width=True)


    # ================= BRANCH PERFORMANCE =================

    st.subheader("   Branch Placement Contribution")

    branch_perf = df[df["Status"]=="Placed"].groupby("Branch")["StudentID"].nunique().reset_index()

    fig5 = px.pie(
        branch_perf,
        names="Branch",
        values="StudentID",
        hole=0.4,
        template="plotly_white"
    )

    st.plotly_chart(fig5, use_container_width=True)

    # ================= TOP COMPANIES =================

    st.subheader("   Top Hiring Companies")

    top_companies = df[df["Status"]=="Placed"]["Company"].value_counts().head(10).reset_index()
    top_companies.columns = ["Company","Placements"]

    fig6 = px.bar(
        top_companies,
        x="Company",
        y="Placements",
        template="plotly_white"
    )

    st.plotly_chart(fig6, use_container_width=True)



# =======================
# STUDENT DASHBOARD
# =======================   
if selected_tab == "Student Dashboard":

    st.markdown("##  Student Intelligence Portal")

    # =========================
    # SEARCH + LOAD (UNCHANGED)
    # =========================
    if role != "Student":
        search = st.text_input("Search by ID / Name")

        filtered_df = df.copy()

        if search:
            filtered_df = filtered_df[
                filtered_df["StudentID"].astype(str).str.contains(search, na=False) |
                filtered_df["Name"].str.contains(search, case=False, na=False)
            ]

        selected_student = st.selectbox(
            "Select Student",
            ["Select"] + filtered_df["StudentID"].astype(str).tolist()
        )

        if selected_student != "Select":
            st.session_state["selected_student"] = selected_student
    else:
        selected_student = student_id
        st.session_state["selected_student"] = selected_student

    selected_student = st.session_state.get("selected_student")

    if not selected_student:
        st.info("Please select a student")
    else:

        stu_data = df[df["StudentID"].astype(str) == str(selected_student)]

        if stu_data.empty:
            st.warning("No data found")
        else:
            profile = stu_data.iloc[0]


            # =========================
            # GLOBAL CALCULATIONS (UNCHANGED)
            # =========================
            sgpas = np.array([profile[f"SGPA_Sem{i}"] for i in range(1,9)])
            backlogs_arr = np.array([profile[f"Backlogs_Sem{i}"] for i in range(1,9)])
            attendance = np.array([profile[f"Attendance_Sem{i}"] for i in range(1,9)])

            avg_sgpa = sgpas.mean()
            total_backlogs = backlogs_arr.sum()
            avg_att = attendance.mean()

            df["Avg_SGPA"] = df[[f"SGPA_Sem{i}" for i in range(1,9)]].mean(axis=1)
            class_avg = df["Avg_SGPA"].mean()

            rank_series = df["Avg_SGPA"].rank(ascending=False)
            student_rank = int(rank_series[df["StudentID"] == profile["StudentID"]].values[0])
            percentile = round((1 - student_rank/len(df)) * 100,2)

            skills = str(profile.get("Skills","")).split(",")

            score = placement_score(profile)

            # =========================
            # MAIN TABS
            # =========================
            tabs = st.tabs([
                "Overview",
                "Academics",
                "Skills & Activities",
                "Placements",
                "AI Insights"
            ])

            # ==========================================================
            # OVERVIEW (FULL)
            # ==========================================================
            with tabs[0]:

                # =========================
                #  MAIN LAYOUT (LEFT - CENTER - RIGHT)
                # =========================
                left, center, right = st.columns([1.2, 3, 1.3])

                # =========================
                #  LEFT PROFILE PANEL
                # =========================
                with left:
                    st.markdown('<div class="glass">', unsafe_allow_html=True)

                    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=110)

                    st.markdown(f"### {profile['Name']}")
                    st.caption(f"{profile['Branch']}")

                    st.write(f" {profile['StudentID']}")
                    st.write(f" {profile['Status']}")

                    st.markdown("---")

                    st.metric("CGPA", round(avg_sgpa,2))
                    st.metric("Backlogs", int(total_backlogs))
                    st.metric("Attendance", round(avg_att,2))

                    st.markdown('</div>', unsafe_allow_html=True)

                # =========================
                #  CENTER PANEL
                # =========================
                with center:

                    # KPI STRIP
                    c1,c2,c3,c4 = st.columns(4)
                    c1.metric("Skills", len(skills))
                    c2.metric("Hackathons", profile["Hackathons"])
                    c3.metric("Papers", profile["Papers"])
                    c4.metric("Conferences", profile["Conferences"])

                    # PROCESS FLOW
                    st.markdown('<div class="glass">', unsafe_allow_html=True)

                    steps = ["Profile","Skills","Aptitude","Interview","Placement"]
                    progress = int(score // 20)

                    flow_html = ""
                    for i, step in enumerate(steps):
                        color = "#6366f1" if i <= progress else "#374151"
                        flow_html += f'<span style="padding:8px 12px;background:{color};margin:4px;border-radius:8px;color:white;">{step}</span>'

                    st.markdown("### Placement Journey")
                    st.markdown(flow_html, unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)

                    # SGPA + ATTENDANCE
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown('<div class="glass">', unsafe_allow_html=True)
                        st.markdown("### SGPA Trend")

                        st.plotly_chart(
                            px.line(pd.DataFrame({"Sem":range(1,9),"SGPA":sgpas}),
                                    x="Sem",y="SGPA",markers=True),
                            use_container_width=True
                        )
                        st.markdown('</div>', unsafe_allow_html=True)

                    with col2:
                        st.markdown('<div class="glass">', unsafe_allow_html=True)
                        st.markdown("### Attendance Trend")

                        st.plotly_chart(
                            px.line(pd.DataFrame({"Sem":range(1,9),"Attendance":attendance}),
                                    x="Sem",y="Attendance"),
                            use_container_width=True
                        )
                        st.markdown('</div>', unsafe_allow_html=True)

                    # SUBJECT ANALYSIS
                    st.markdown('<div class="glass">', unsafe_allow_html=True)

                    st.markdown("### Subject Intelligence")

                    subject_cols = [c for c in df.columns if "_Sem" in c and not any(x in c for x in ["SGPA","Attendance","Backlogs"])]

                    sem = st.selectbox("Semester", [1,2,3,4,5,6,7,8], key="profile_sem")

                    cols = [c for c in subject_cols if f"_Sem{sem}" in c]
                    sub = [c.replace(f"_Sem{sem}","") for c in cols]
                    marks = [profile[c] for c in cols]

                    sdf = pd.DataFrame({"Subject":sub,"Marks":marks})

                    c1,c2 = st.columns(2)
                    c1.plotly_chart(
                        px.bar(sdf, x="Subject", y="Marks"),
                        use_container_width=True,
                        key="subject_bar_chart"
                    )

                    c2.plotly_chart(
                        px.line_polar(sdf, r="Marks", theta="Subject", line_close=True),
                        use_container_width=True,
                        key="subject_radar_chart"
                    )

                    st.markdown('</div>', unsafe_allow_html=True)

                    # SKILLS + ACTIVITIES
                    st.markdown('<div class="glass">', unsafe_allow_html=True)

                    chip_html = "".join([f'<span class="chip">{s}</span>' for s in skills])
                    st.markdown("### Skills")
                    st.markdown(chip_html, unsafe_allow_html=True)

                    activity_df = pd.DataFrame({
                        "Type":["Sports","Clubs"],
                        "Value":[profile["Sports"],profile["Clubs"]]
                    })

                    st.plotly_chart(px.pie(activity_df,names="Type",values="Value"),use_container_width=True)

                    st.markdown('</div>', unsafe_allow_html=True)

                    # CORRELATION
                    st.markdown('<div class="glass">', unsafe_allow_html=True)

                    st.markdown("### Data Intelligence")
                    num_df = df.select_dtypes(include=np.number)
                    st.plotly_chart(px.imshow(num_df.corr()), use_container_width=True)

                    st.markdown('</div>', unsafe_allow_html=True)

                # =========================
                #  RIGHT PANEL
                # =========================
                with right:

                    import calendar, datetime

                    st.markdown('<div class="glass">', unsafe_allow_html=True)
                    st.markdown("###  Calendar")

                    today = datetime.date.today()
                    st.text(calendar.month(today.year, today.month))

                    st.markdown('</div>', unsafe_allow_html=True)

                    # ACHIEVEMENTS
                    st.markdown('<div class="glass">', unsafe_allow_html=True)

                    total_ach = profile["Hackathons"] + profile["Papers"] + profile["Conferences"]

                    st.metric("Achievements", total_ach)
                    st.progress(min(total_ach/10,1))

                    st.markdown('</div>', unsafe_allow_html=True)

                    # AI INSIGHT
                    st.markdown('<div class="glass">', unsafe_allow_html=True)

                    st.markdown("### AI Insight")
                    st.info(ai_summary(profile))

                    st.markdown('</div>', unsafe_allow_html=True)

                # =========================
                #  FULL DATA (NO LOSS)
                # =========================
                with st.expander("View All Attributes"):
                    st.dataframe(profile.to_frame(name="Value"))

            # ==========================================================
            # ACADEMICS (FULL  NOTHING REMOVED)
            # ==========================================================
            with tabs[1]:

                # KPIs
                c1,c2,c3,c4,c5 = st.columns(5)
                c1.metric("SGPA", round(avg_sgpa,2))
                c2.metric("Class Avg", round(class_avg,2))
                c3.metric("Rank", student_rank)
                c4.metric("Percentile", f"{percentile}%")
                c5.metric("Backlogs", int(total_backlogs))

                # Comparison
                comp_df = pd.DataFrame({
                    "Type": ["Student","Class"],
                    "SGPA": [avg_sgpa, class_avg]
                })
                st.plotly_chart(px.bar(comp_df,x="Type",y="SGPA"), use_container_width=True)

                # Trend
                sem_df = pd.DataFrame({"Semester":range(1,9),"SGPA":sgpas})
                st.plotly_chart(px.line(sem_df,x="Semester",y="SGPA",markers=True),
                                use_container_width=True)

                # Prediction
                growth = (sgpas[-1]-sgpas[0])/7
                predicted = sgpas[-1] + growth
                st.metric("Predicted SGPA", round(predicted,2))

                # DOMAIN INTELLIGENCE (YOUR ORIGINAL LOOP)
                subject_cols = [c for c in df.columns if "_Sem" in c and not any(x in c for x in ["SGPA","Attendance","Backlogs"])]

                domain_scores = {"AI/ML":0,"Core CS":0,"Finance":0}

                for col in subject_cols:
                    val = profile[col]
                    name = col.lower()

                    if "ai" in name:
                        domain_scores["AI/ML"] += val
                    elif "db" in name or "os" in name:
                        domain_scores["Core CS"] += val
                    elif "finance" in name:
                        domain_scores["Finance"] += val

                best_domain = max(domain_scores, key=domain_scores.get)
                st.success(f"Best Domain: {best_domain}")

                # SUBJECT ANALYSIS
                sem = st.selectbox(
                    "Semester",
                    [1,2,3,4,5,6,7,8],
                    key="overview_sem"
                )

                cols = [c for c in df.columns if f"_Sem{sem}" in c and not any(x in c for x in ["SGPA","Attendance","Backlogs"])]
                sub = [c.replace(f"_Sem{sem}","") for c in cols]
                marks = [profile[c] for c in cols]

                sdf = pd.DataFrame({"Subject":sub,"Marks":marks})

                col1,col2 = st.columns(2)
                col1.plotly_chart(px.bar(sdf,x="Subject",y="Marks"),use_container_width=True)

                fig = px.line_polar(sdf,r="Marks",theta="Subject",line_close=True)
                col2.plotly_chart(fig, use_container_width=True)

                # DISTRIBUTION
                st.plotly_chart(px.histogram(df,x="Avg_SGPA"), use_container_width=True)

                # RISK
                if avg_sgpa < class_avg:
                    st.warning("Below class average")
                if total_backlogs > 0:
                    st.warning("Backlogs present")

                # EXPORT
                report = f"SGPA:{avg_sgpa}, Rank:{student_rank}, Domain:{best_domain}"
                st.download_button("Download Report", report, "report.txt")

            # ==========================================================
            # SKILLS & ACTIVITIES (FULL)
            # ==========================================================
            with tabs[2]:

                skill_df = pd.DataFrame({
                    "Skill": skills,
                    "Level": [80 + 5*i for i in range(len(skills))]
                })

                st.plotly_chart(px.bar(skill_df,x="Skill",y="Level"),use_container_width=True)

                st.metric("Hackathons", profile["Hackathons"])
                st.metric("Papers", profile["Papers"])
                st.metric("Conferences", profile["Conferences"])

                activity_df = pd.DataFrame({
                    "Type": ["Sports","Clubs"],
                    "Count": [profile["Sports"], profile["Clubs"]]
                })

                st.plotly_chart(px.pie(activity_df,names="Type",values="Count"),use_container_width=True)

                strength = (
                    len(skills)*10 +
                    profile["Hackathons"]*5 +
                    profile["Papers"]*8 +
                    profile["Conferences"]*6 +
                    profile["Sports"]*3 +
                    profile["Clubs"]*3
                )
                strength = min(strength,100)

                st.progress(strength/100)
                st.metric("Strength", f"{strength}%")

            # ==========================================================
            # PLACEMENTS (FULL)
            # ==========================================================
            with tabs[3]:

                total_attempts = len(stu_data)
                placed = len(stu_data[stu_data["Status"]=="Placed"])
                rejected = len(stu_data[stu_data["Status"]=="Rejected"])

                success_ratio = round((placed/total_attempts)*100,2) if total_attempts else 0

                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Attempts", total_attempts)
                c2.metric("Offers", placed)
                c3.metric("Rejected", rejected)
                c4.metric("Success %", f"{success_ratio}%")

                st.plotly_chart(px.pie(names=["Placed","Rejected"],values=[placed,rejected]))

                st.plotly_chart(px.bar(stu_data,x="Company",y="Package",color="Status"))

                if not stu_data.empty:
                    top_offer = stu_data.sort_values("Package", ascending=False).iloc[0]
                    st.success(f"Top Offer: {top_offer['Company']} - {top_offer['Package']} LPA")

                if "Placed_Date" in stu_data.columns:
                    st.plotly_chart(px.scatter(stu_data,x="Placed_Date",y="Company",size="Package"))

                st.dataframe(stu_data)

                avg_package = stu_data["Package"].mean() if not stu_data.empty else 0
                st.metric("Average Package", round(avg_package,2))

            # ==========================================================
            # AI INSIGHTS (FULL)
            # ==========================================================
            with tabs[4]:

                file = st.file_uploader("Upload Resume")

                if file:
                    text = file.read().decode(errors="ignore")
                    st.metric("Resume Score", min(len(text.split())/8,100))

                company = st.selectbox("Company",
                    ["Google","Amazon","Infosys","TCS","Wipro"])

                base = placement_score(profile)

                adj = base - 20 if company in ["Google","Amazon"] else base + 10
                adj = max(0,min(adj,100))

                st.metric("Selection Probability", f"{adj}%")
                st.progress(adj/100)

                st.info(ai_summary(profile))
# =======================
# ADMIN COMPANY ANALYSIS
# =======================

if selected_tab == "Admin Company Analysis":
    # ============================================================
    # YOUR EXISTING COMPANY ANALYTICS (UNCHANGED)
    # ============================================================

    st.markdown("---")
    st.subheader("   Company-wise Selection Analysis")

    company_year = df[df["Status"]=="Placed"].groupby(["Year","Company"])["StudentID"].nunique().reset_index()

    fig3 = px.bar(company_year, x="Company", y="StudentID", color="Year",
                  template="plotly_white",
                  title="Company-wise Placements per Year")
    st.plotly_chart(fig3, use_container_width=True)


# -----------------------------------------------------
# 1. COMPANY HIRING PERFORMANCE ANALYSIS
# -----------------------------------------------------
    st.markdown("### 1   Company Hiring Performance")

    company_perf = df.groupby("Company").agg(
        Applicants=("StudentID","count"),
        Selected=("Status",lambda x:(x=="Placed").sum())
    ).reset_index()

    company_perf["Selection Rate %"] = round(
        (company_perf["Selected"]/company_perf["Applicants"])*100,2
    )

    fig = px.bar(
        company_perf,
        x="Company",
        y="Selected",
        color="Selection Rate %",
        title="Company vs Selected Students"
    )
    st.plotly_chart(fig, use_container_width=True)


    # -----------------------------------------------------
    # 6. COMPANY VISIT TREND
    # -----------------------------------------------------
    st.markdown("### 6   Company Visit Trend")

    company_year = df.groupby(["Year","Company"])["StudentID"].count().reset_index()

    fig = px.line(
        company_year,
        x="Year",
        y="StudentID",
        color="Company",
        title="Company Visits Over Years"
    )
    st.plotly_chart(fig,use_container_width=True)




    # -----------------------------------------------------
    # 8. INTERNSHIP TO PPO CONVERSION
    # -----------------------------------------------------
    st.markdown("### 8   Internship to PPO Conversion")

    temp_df = df.groupby("Year")["Package"].mean().reset_index()

    fig = px.line(
        temp_df,
        x="Year",
        y="Package",
        markers=True
    )

    fig.update_traces(
        mode="lines+markers",
        line=dict(width=3),
        marker=dict(size=8)
    )

    fig.update_layout(
        template="plotly_white",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


    # -----------------------------------------------------
    # 10. SKILL DEMAND ANALYSIS
    # -----------------------------------------------------
    st.markdown("###    Skill Demand Analysis")

    skills = df["Skills"].str.split(",",expand=True).stack().value_counts().reset_index()
    skills.columns = ["Skill","Count"]

    fig = px.bar(
        skills.head(10),
        x="Skill",
        y="Count",
        title="Top Skills Required by Companies"
    )
    st.plotly_chart(fig,use_container_width=True)



    # -----------------------------------------------------
    # 15. TOP PAYING COMPANIES
    # -----------------------------------------------------
    st.markdown("### 1  5   Top Paying Companies")

    top_pay = placed_df.groupby("Company")["Package"].max().reset_index()

    fig = px.bar(
        top_pay.sort_values("Package",ascending=False).head(10),
        x="Company",
        y="Package",
        title="Top Paying Companies"
    )
    st.plotly_chart(fig,use_container_width=True)



if selected_tab == "Company Dashboard":

    st.markdown("## Company Intelligence Portal")

    comp_df = None  #  ALWAYS DEFINE FIRST

    # ======================================================
    # ROLE BASED COMPANY VIEW
    # ======================================================

    if role == "Admin":

        selected_company = st.session_state.get("company", None)

        if selected_company is None:
            st.error("Session expired. Please login again.")
            

        st.success(f"Logged in as {selected_company} Admin")

        comp_df = df[df["Company"] == selected_company]

    else:

        st.markdown("### Select Company")

        search_company = st.text_input("Search Company")

        filtered_df = df.copy()

        if search_company:
            filtered_df = filtered_df[
                filtered_df["Company"].str.contains(search_company, case=False, na=False)
            ]

        company_list = sorted(filtered_df["Company"].dropna().unique().tolist())

        selected_company = st.selectbox(
            "Select Company",
            ["Select Company"] + company_list
        )

        if selected_company == "Select Company":
            st.info("Please select a company")
            

        else:
            st.session_state["selected_company"] = selected_company
            comp_df = df[df["Company"] == selected_company]
            st.success(f"Loaded Company: {selected_company}")

    # ======================================================
    # FINAL SAFETY CHECK
    # ======================================================

    if comp_df is None or comp_df.empty:
        st.warning("No data available")
        st.stop()

    # ======================================================
    # DISPLAY DATA (SAFE)
    # ======================================================

    st.dataframe(comp_df)

    # ======================================================
    # KPI DASHBOARD (GLASS STYLE)
    # ======================================================

    total = len(comp_df)
    placed = len(comp_df[comp_df["Status"] == "Placed"])
    rejected = len(comp_df[comp_df["Status"] == "Rejected"])
    success = round((placed / total) * 100, 2) if total else 0

    avg_package = round(comp_df[comp_df["Status"] == "Placed"]["Package"].mean(), 2) if placed else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Applicants", total)
    k2.metric("Selected", placed)
    k3.metric("Rejected", rejected)
    k4.metric("Success %", f"{success}%")
    k5.metric("Avg Package", f"{avg_package} LPA")

    st.markdown("---")

    # ======================================================
    # SUB TABS
    # ======================================================

    company_tabs = st.tabs([
        " Overview",
        " Hiring Intelligence",
        " Salary",
        " Students",
        " AI Insights"
    ])

    # ======================================================
    # OVERVIEW
    # ======================================================
    with company_tabs[0]:

        st.subheader(" Selection Distribution")

        st.plotly_chart(
            px.pie(
                names=["Selected", "Rejected"],
                values=[placed, rejected],
                hole=0.6
            ),
            use_container_width=True
        )

        st.subheader(" Year-wise Hiring")

        yearly = comp_df.groupby("Year")["StudentID"].count().reset_index()

        st.plotly_chart(
            px.line(yearly, x="Year", y="StudentID", markers=True),
            use_container_width=True
        )

    # ======================================================
    # HIRING INTELLIGENCE
    # ======================================================
    with company_tabs[1]:

        st.subheader(" Branch Hiring")

        branch = comp_df.groupby("Branch")["StudentID"].count().reset_index()

        st.plotly_chart(
            px.bar(branch, x="Branch", y="StudentID"),
            use_container_width=True
        )

        st.subheader(" Selection Success %")

        branch_sel = comp_df.groupby("Branch").apply(
            lambda x: (x["Status"] == "Placed").sum() / len(x) * 100
        ).reset_index(name="Success %")

        st.plotly_chart(
            px.bar(branch_sel, x="Branch", y="Success %"),
            use_container_width=True
        )

    # ======================================================
    # SALARY
    # ======================================================
    with company_tabs[2]:

        placed_df = comp_df[comp_df["Status"] == "Placed"].copy()

        if not placed_df.empty:

            c1, c2, c3 = st.columns(3)

            c1.metric("Avg", round(placed_df["Package"].mean(), 2))
            c2.metric("Max", placed_df["Package"].max())
            c3.metric("Min", placed_df["Package"].min())

            st.plotly_chart(
                px.box(placed_df, y="Package"),
                use_container_width=True
            )

        else:
            st.warning("No salary data")

    # ======================================================
    # STUDENTS
    # ======================================================
    with company_tabs[3]:

        placed_df = comp_df[comp_df["Status"] == "Placed"].copy()

        st.subheader(" Top Students")

        top_students = placed_df.sort_values("Package", ascending=False).head(10)

        st.dataframe(
            top_students[["Name", "Branch", "Package"]],
            use_container_width=True
        )

        st.subheader(" Skill Demand")

        skills = comp_df["Skills"].str.split(",", expand=True).stack().value_counts().reset_index()
        skills.columns = ["Skill", "Count"]

        st.plotly_chart(
            px.bar(skills.head(10), x="Skill", y="Count"),
            use_container_width=True
        )

    # ======================================================
    # AI INSIGHTS
    # ======================================================
    with company_tabs[4]:

        placed_df = comp_df[comp_df["Status"] == "Placed"]

        if not placed_df.empty:

            top_branch = placed_df["Branch"].value_counts().idxmax()
            avg_package = placed_df["Package"].mean()

            st.success(f"Top Hiring Branch: {top_branch}")
            st.success(f"Average Package: {round(avg_package, 2)} LPA")

        difficulty = round(len(comp_df) / max(len(placed_df), 1), 2)
        st.warning(f"Hiring Difficulty Score: {difficulty}")

        st.markdown("###  Ask AI")

        q = st.text_input("Ask about this company")

        if q:
            answer = gpt_ai_engine(q, comp_df)
            st.info(answer)

if selected_tab == "New Company Drive":
    st.success("Register New Company Drive")

    # ===============================
    # COMPANY DRIVE REGISTRATION
    # ===============================

    with st.expander("   Register New Company Drive"):

        st.subheader("1   Basic Company Information")

        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input("Company Name")
            company_website = st.text_input("Company Website")
            company_location = st.text_input("Company Location")
            industry_type = st.selectbox("Industry Type",
                                         ["IT","Finance","Consulting","Manufacturing","Other"])
            year_established = st.number_input("Year of Establishment",1950,2026)

        with col2:
            employees = st.number_input("Number of Employees",1,100000)
            company_desc = st.text_area("Company Description")
            contact_person = st.text_input("Contact Person Name")
            designation = st.text_input("Designation")
            email = st.text_input("Email ID")
            phone = st.text_input("Phone Number")


        # ===============================
        # JOB ROLE DETAILS
        # ===============================

        st.subheader("2   Job Role Details")

        col3, col4 = st.columns(2)

        with col3:
            job_title = st.text_input("Job Title / Role")
            department = st.selectbox("Department",
                                      ["IT","HR","Marketing","Finance","Other"])
            job_type = st.selectbox("Job Type",
                                    ["Full Time","Internship","Internship + PPO"])
            vacancies = st.number_input("Number of Vacancies",1,500)

        with col4:
            work_location = st.text_input("Work Location")
            bond = st.selectbox("Service Agreement",
                                ["No Bond","1 Year","2 Years"])
            job_desc = st.text_area("Job Description")


        # ===============================
        # SALARY & BENEFITS
        # ===============================

        st.subheader("3   Salary & Benefits")

        col5, col6 = st.columns(2)

        with col5:
            ctc = st.number_input("CTC (LPA)",0.0,50.0)
            inhand = st.number_input("In-Hand Salary",0.0,200000.0)
            training_salary = st.number_input("Training Period Salary",0.0,100000.0)

        with col6:
            bonus = st.text_input("Bonus / Incentives")
            health = st.selectbox("Health Insurance",["Yes","No"])
            accommodation = st.selectbox("Accommodation",["Yes","No"])
            travel = st.selectbox("Travel Allowance",["Yes","No"])


        # ===============================
        # ELIGIBILITY
        # ===============================

        st.subheader("4   Eligibility Criteria")

        eligible_branches = st.multiselect(
            "Eligible Branches",
            ["CSE","IT","ECE","EEE","Mechanical","Civil","AI & DS"]
        )

        min_cgpa = st.slider("Minimum CGPA",5.0,10.0,6.5)
        backlogs_allowed = st.number_input("Allowed Backlogs",0,10)

        skills_required = st.text_area("Required Skills")


        # ===============================
        # SELECTION PROCESS
        # ===============================

        st.subheader("5   Selection Process")

        rounds = st.multiselect(
            "Recruitment Rounds",
            ["Online Test","Coding Test","Group Discussion",
             "Technical Interview","HR Interview"]
        )

        test_platform = st.selectbox(
            "Test Platform",
            ["HackerRank","AMCAT","CoCubes","Company Portal","Other"]
        )

        interview_mode = st.selectbox(
            "Interview Mode",
            ["Online","Offline"]
        )


        # ===============================
        # RECRUITMENT SCHEDULE
        # ===============================

        st.subheader("6   Recruitment Schedule")

        ppt_date = st.date_input("Pre Placement Talk Date")
        test_date = st.date_input("Online Test Date")
        interview_date = st.date_input("Interview Date")
        offer_date = st.date_input("Offer Release Date")
        joining_date = st.date_input("Joining Date")


        # ===============================
        # DOCUMENTS REQUIRED
        # ===============================

        st.subheader("7   Documents Required")

        documents = st.multiselect(
            "Documents",
            ["Resume","Academic Mark Sheets","ID Proof",
             "Passport Photo","Portfolio/GitHub"]
        )


        # ===============================
        # INTERNAL PLACEMENT TRACKING
        # ===============================

        st.subheader("8   Placement Cell Internal Tracking")

        company_id = st.text_input("Company ID")
        drive_id = st.text_input("Drive ID")

        drive_status = st.selectbox(
            "Drive Status",
            ["Upcoming","Ongoing","Completed"]
        )

        applied = st.number_input("Students Applied",0,5000)
        shortlisted = st.number_input("Students Shortlisted",0,5000)
        selected = st.number_input("Students Selected",0,5000)


        # ===============================
        # SAVE BUTTON
        # ===============================

        if st.button("Save Company Drive", key="save_drive"):

            company_data = {
                "Company": company_name,
                "CTC": ctc,
                "Vacancies": vacancies,
                "Branches": eligible_branches,
                "Min CGPA": min_cgpa,
                "Rounds": rounds,
                "Drive Status": drive_status,
                "Selected Students": selected
            }

            import os

            file_path = "company_drives.csv"

            new_data = pd.DataFrame([company_data])

            if os.path.exists(file_path):
                new_data.to_csv(file_path, mode='a', header=False, index=False)
            else:
                new_data.to_csv(file_path, index=False)

            st.success("   Company Drive Registered Successfully")
            st.json(company_data)


# ==========================================================
# COMMUNICATION ANALYZER
# ==========================================================
# ==========================================================
# COMMUNICATION ANALYZER (FINAL CLEAN VERSION)
# ==========================================================
if selected_tab == "Communication Analyzer":

    import tempfile, wave, re, time
    import numpy as np
    from pydub import AudioSegment
    import speech_recognition as sr
    from textblob import TextBlob

    st.title("AI Interview Communication Analyzer")
    st.caption("Real-time + HR-level evaluation system")

    audio = audiorecorder("Start Recording", "Stop Recording")

    if len(audio) > 0:

        with st.spinner("Processing your speech..."):

            # =========================
            # AUDIO PROCESSING
            # =========================
            audio_bytes = audio.export(format="wav").read()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio_bytes)
                filename = f.name

            try:
                sound = AudioSegment.from_file(filename)
                sound = sound.set_frame_rate(16000).set_channels(1)
                sound = sound.normalize()
                sound.export(filename, format="wav")
            except Exception as e:
                st.error(f"Audio processing error: {e}")
                st.stop()

            st.audio(audio_bytes)

            # =========================
            # SPEECH TO TEXT
            # =========================
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True

            try:
                with sr.AudioFile(filename) as source:
                    audio_data = recognizer.record(source)

                text = recognizer.recognize_google(audio_data, language="en-IN")

                if not text.strip():
                    st.warning("No speech detected. Try again.")
                    st.stop()

                st.success("Transcription:")
                st.write(text)

            except Exception as e:
                st.error(f"Speech recognition failed: {e}")
                st.stop()

        # =========================
        # TEXT PROCESSING
        # =========================
        words = text.lower().split()
        total_words = len(words)

        if total_words == 0:
            st.warning("No valid words detected.")
            st.stop()

        # =========================
        # AI CORRECTION
        # =========================
        try:
            corrected = call_gemini(f"""
Correct this speech transcript:

{text}

Make it professional and grammatically correct.
""")
            st.write("Corrected:", corrected)
        except:
            st.warning("AI correction unavailable")

        # =========================
        # AUDIO METRICS
        # =========================
        with wave.open(filename, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            channels = wf.getnchannels()

            duration = frames / float(rate)
            raw_signal = wf.readframes(frames)

            if len(raw_signal) == 0:
                st.error("Empty audio")
                st.stop()

            signal = np.frombuffer(raw_signal, dtype=np.int16)

            if channels == 2:
                signal = signal[::2]

        energy = np.mean(np.abs(signal)) if len(signal) > 0 else 0

        # =========================
        # METRICS CALCULATION
        # =========================
        wpm = (total_words / duration) * 60 if duration > 0 else 0
        voice_conf = min(100, energy / 300)

        fillers = ["um","uh","like","basically","actually"]
        filler_count = sum(words.count(f) for f in fillers)
        filler_score = max(0, 100 - filler_count * 5)

        unique_words = len(set(words))
        fluency = round((unique_words / total_words) * 100, 2)

        clarity = min(100, total_words * 2)

        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        structure = min(100, (total_words / len(sentences))*6 if sentences else 0)

        pro_words = ["project","developed","implemented","experience","analysis"]
        pro_score = min(100, sum(1 for w in words if w in pro_words)*10)

        pause_score = max(0, 100 - (text.count(",") + text.count("..."))*5)

        # =========================
        # EMOTION ANALYSIS
        # =========================
        polarity = TextBlob(text).sentiment.polarity

        if polarity > 0.3:
            emotion = "Confident"
        elif polarity < -0.2:
            emotion = "Nervous"
        else:
            emotion = "Neutral"

        confidence_score = round((voice_conf * 0.6 + fluency * 0.4), 2)

        # =========================
        # SPEED SCORE
        # =========================
        if 110 <= wpm <= 160:
            speed_score = 100
        elif wpm < 110:
            speed_score = 60
        else:
            speed_score = 70

        # =========================
        # FINAL SCORE
        # =========================
        final_score = round((
            fluency*0.15 +
            filler_score*0.1 +
            clarity*0.1 +
            structure*0.1 +
            pro_score*0.1 +
            pause_score*0.1 +
            voice_conf*0.1 +
            speed_score*0.1 +
            confidence_score*0.15
        ), 2)

        # =========================
        # LIVE SIMULATION
        # =========================
        st.subheader("Live Simulation")

        live_box = st.empty()

        for i in range(1, len(words)+1):
            partial = " ".join(words[:i])

            live_fluency = min(100, (len(set(words[:i]))/(i+1))*100)
            live_score = round((live_fluency*0.5 + min(100,i*2)*0.5),2)

            with live_box.container():
                st.write(partial)
                c1,c2 = st.columns(2)
                c1.metric("Fluency", f"{round(live_fluency,1)}%")
                c2.metric("Score", f"{live_score}%")
                st.progress(live_score/100)

            time.sleep(0.01)

        # =========================
        # SCORECARD
        # =========================
        st.subheader("Interview Scorecard")

        c1,c2,c3 = st.columns(3)
        c1.metric("Confidence", f"{confidence_score}%")
        c2.metric("Fluency", f"{fluency}%")
        c3.metric("Clarity", f"{clarity}%")

        c4,c5,c6 = st.columns(3)
        c4.metric("Filler Control", f"{filler_score}%")
        c5.metric("Professional Language", f"{pro_score}%")
        c6.metric("Structure", f"{structure}%")

        c7,c8,c9 = st.columns(3)
        c7.metric("Thinking Flow", f"{pause_score}%")
        c8.metric("Voice Confidence", f"{round(voice_conf,1)}%")
        c9.metric("Speech Speed", f"{round(wpm,1)} WPM")

        st.metric("Overall Score", f"{final_score}%")
        st.progress(final_score/100)

        st.info(f"Emotion: {emotion}")

        # =========================
        # AI FEEDBACK
        # =========================
        st.subheader("AI Interview Feedback")

        try:
            prompt = f"""
You are an HR interviewer.

Evaluate this answer:

{text}

Give:
- Strengths
- Weaknesses
- Improvements
- Final Verdict
"""
            response = model.generate_content(prompt)
            st.success(response.text)

        except Exception as e:
            st.error(f"AI Error: {e}")

        # =========================
        # INSIGHTS
        # =========================
        st.subheader("Insights")

        if wpm < 110:
            st.warning("Speak faster")
        elif wpm > 160:
            st.warning("Slow down")

        if voice_conf < 40:
            st.warning("Increase voice confidence")

        if filler_score < 70:
            st.warning("Reduce filler words")

        if final_score > 80:
            st.success("Excellent performance")

        # =========================
        # DOWNLOAD REPORT
        # =========================
        report = f"""
AI INTERVIEW REPORT

{text}

Confidence: {confidence_score}
Fluency: {fluency}
Clarity: {clarity}
WPM: {wpm}
Score: {final_score}

Emotion: {emotion}
"""

        st.download_button("Download Report", report, file_name="report.txt")

# ==========================================================
# ENTERPRISE AI MOCK INTERVIEW SYSTEM
# ==========================================================
if selected_tab == "Mock Interview":

    import streamlit as st
    import time, re

    # ================= SESSION =================
    if "mock" not in st.session_state:
        st.session_state.mock = {
            "active": False,
            "question": "",
            "answer": "",
            "logs": [],
            "level": "Beginner",
            "role": "",
            "subject": "",
            "report": None,
            "q_no": 1
        }

    data = st.session_state.mock

    # ================= SIDEBAR CONFIG =================
    with st.sidebar:
        st.title(" Interview Setup")

        data["role"] = st.selectbox("Role", [
            "Software Engineer",
            "Data Analyst",
            "AI Engineer",
            "Data Scientist",
            "Web Developer"
        ])

        data["subject"] = st.selectbox("Subject", [
            "General",
            "DSA",
            "DBMS",
            "OOP",
            "SQL",
            "Python",
            "Machine Learning"
        ])

        data["level"] = st.selectbox("Level", [
            "Beginner",
            "Easy",
            "Medium",
            "Hard",
            "Advanced"
        ])

        if st.button("Start Interview"):
            data["active"] = True
            data["q_no"] = 1

            data["question"] = call_gemini(f"""
You are an interviewer.

Role: {data["role"]}
Subject: {data["subject"]}
Difficulty: {data["level"]}

Generate ONLY one interview question.
No explanation. Only question.
""")

            data["question"] = data["question"].split("\n")[0]
            st.rerun()

    # ================= MAIN UI =================
    if data["active"]:

        st.title(" AI Mock Interview")

        st.markdown(f"""
###  Role: **{data["role"]}**
###  Subject: **{data["subject"]}**
###  Level: **{data["level"]}**
###  Question #{data["q_no"]}
        """)

        st.info(data["question"])

        # ================= ANSWER =================
        data["answer"] = st.text_area("Your Answer", height=200)

        col1, col2, col3 = st.columns(3)

        # ================= SUBMIT =================
        if col1.button("Submit Answer"):

            if not data["answer"].strip():
                st.warning("Please enter your answer")
            else:

                feedback = call_gemini(f"""
Evaluate this answer.

Question: {data["question"]}
Answer: {data["answer"]}

Give:
Score: X/10
Strengths:
Weakness:
Improvement:
""")

                st.success("Evaluation")
                st.write(feedback)

                data["logs"].append({
                    "q": data["question"],
                    "a": data["answer"],
                    "f": feedback
                })

        # ================= NEXT =================
        if col2.button("Next Question"):

            data["q_no"] += 1

            data["question"] = call_gemini(f"""
Previous Question: {data["question"]}
Answer: {data["answer"]}

Generate next question.

Role: {data["role"]}
Subject: {data["subject"]}
Difficulty: {data["level"]}

Keep it clear and practical.
""")

            data["question"] = data["question"].split("\n")[0]
            data["answer"] = ""

            st.rerun()

        # ================= END =================
        if col3.button("End Interview"):

            data["report"] = call_gemini(f"""
Interview Logs:
{data["logs"]}

Generate final report:

Overall Score /10
Strengths
Weaknesses
Improvement Plan
Final Verdict
""")

            data["active"] = False
            st.rerun()

        # ================= PROGRESS =================
        st.progress(min(data["q_no"] * 10, 100))

    # ================= REPORT =================
    elif data["report"]:

        st.title(" Final Report")
        st.success(data["report"])

        if st.button("Restart"):
            del st.session_state["mock"]
            st.rerun()