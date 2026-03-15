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
# ================================
# SESSION INIT
# ================================

if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None

# ================================
# SECRET KEY
# ================================
SECRET_KEY = "PLACEMENT_INTELLIGENCE_APEX_ENTERPRISE_SECURITY_2026"


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

        st.markdown('<div class="login-box">', unsafe_allow_html=True)

        st.title("   Placement Intelligence Apex")
        st.caption("AI Powered Placement Analytics Portal")

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


# =======================
# LOAD CSV DATA
# =======================

@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv("PLACEMENT_INTELLIGENCE_MASTER_FINAL_LARGE.csv")
    df["Placed_Date"] = pd.to_datetime(df["Placed_Date"], errors="coerce")
    return df

df = load_data()

# ==========================================================
# AI NARRATIVE INTERPRETATION ENGINE
# ==========================================================

def generate_narrative_report(df):

    placed = df[df["Status"] == "Placed"].copy()

    report = {}

    # ---------------- Hiring Performance ----------------
    company_hires = placed["Company"].value_counts()
    top_company = company_hires.idxmax()
    top_count = company_hires.max()

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
# UNIVERSAL DATA ANALYSIS ENGINE
# ============================================================

def dataset_ai_engine(question, df):

    q = question.lower()

    data = df.copy()

    detected_columns = detect_columns(q, df)

    year = detect_year(q)

    if year and "Year" in df.columns:

        data = data[data["Year"] == year]


    # ========================================================
    # MOST / HIGHEST
    # ========================================================

    if "most" in q or "highest" in q or "maximum" in q:

        if "company" in q:

            placed = data[data["Status"] == "Placed"]

            counts = placed["Company"].value_counts()

            company = counts.idxmax()

            count = counts.max()

            return f"{company} hired the most students ({count})."


        if "package" in q:

            row = data.loc[data["Package"].idxmax()]

            return f"""
Highest Package Analysis

Student : {row['Name']}

Company : {row['Company']}

Package :   {row['Package']} LPA
"""


        if "cgpa" in q:

            row = data.loc[data["CGPA"].idxmax()]

            return f"{row['Name']} has the highest CGPA of {row['CGPA']}."


        if "branch" in q:

            placed = data[data["Status"] == "Placed"]

            branch = placed["Branch"].value_counts().idxmax()

            return f"{branch} branch has the highest placements."


    # ========================================================
    # TOP N ANALYSIS
    # ========================================================

    if "top" in q:

        number = re.search(r"\d+", q)

        n = 5

        if number:
            n = int(number.group())

        if "package" in q:

            top = data.sort_values("Package", ascending=False).head(n)

            result = f"Top {n} Highest Packages\n\n"

            for _, r in top.iterrows():

                result += f"{r['Name']} - {r['Company']} -   {r['Package']} LPA\n"

            return result


        if "cgpa" in q:

            top = data.sort_values("CGPA", ascending=False).head(n)

            result = f"Top {n} Students by CGPA\n\n"

            for _, r in top.iterrows():

                result += f"{r['Name']} - {r['CGPA']}\n"

            return result


    # ========================================================
    # COUNT QUERIES
    # ========================================================

    if "how many" in q or "count" in q:

        if "students" in q:

            return f"Total Students : {data['StudentID'].nunique()}"


        if "placed" in q:

            placed = data[data["Status"] == "Placed"]

            return f"Placed Students : {placed['StudentID'].nunique()}"


        if "company" in q:

            return f"Total Companies : {data['Company'].nunique()}"


    # ========================================================
    # AVERAGE ANALYSIS
    # ========================================================

    if "average" in q or "mean" in q:

        if "package" in q:

            avg = data["Package"].mean()

            return f"Average Package :   {round(avg,2)} LPA"


        if "cgpa" in q:

            avg = data["CGPA"].mean()

            return f"Average CGPA : {round(avg,2)}"


    # ========================================================
    # GENERAL DATA EXPLORATION
    # ========================================================

    if detected_columns:

        col = detected_columns[0]

        if data[col].dtype in ["int64","float64"]:

            return f"""
Statistics for {col}

Mean : {round(data[col].mean(),2)}

Max : {data[col].max()}

Min : {data[col].min()}
"""

        else:

            return f"""
Top values for {col}

{data[col].value_counts().head(5)}
"""


    return "I analyzed the dataset but could not fully interpret the question."

# ==========================================================
# UNIVERSAL GRAPH GENERATOR FOR ALL DATASET ATTRIBUTES
# ==========================================================

import plotly.express as px
import re

def universal_graph_ai(question, df):

    q = question.lower()

    columns = df.columns.tolist()

    detected = []

    # Detect columns mentioned in question
    for col in columns:

        col_name = col.lower()

        if col_name in q:
            detected.append(col)

    # Detect graph type
    graph_type = "scatter"

    if "bar" in q:
        graph_type = "bar"

    elif "line" in q or "trend" in q:
        graph_type = "line"

    elif "hist" in q or "distribution" in q:
        graph_type = "hist"

    elif "box" in q:
        graph_type = "box"

    # Detect year filter
    year_match = re.search(r"\b20\d{2}\b", q)

    data = df.copy()

    if year_match and "Year" in df.columns:

        year = int(year_match.group())

        data = data[data["Year"] == year]

    # =========================
    # ONE COLUMN GRAPH
    # =========================

    if len(detected) == 1:

        col = detected[0]

        if graph_type == "hist":

            fig = px.histogram(data, x=col,
                               title=f"{col} Distribution")

        elif graph_type == "box":

            fig = px.box(data, y=col,
                         title=f"{col} Spread")

        else:

            counts = data[col].value_counts().reset_index()

            fig = px.bar(counts,
                         x="index",
                         y=col,
                         title=f"{col} Frequency")

        return fig

    # =========================
    # TWO COLUMN GRAPH
    # =========================

    if len(detected) >= 2:

        x = detected[0]
        y = detected[1]

        if graph_type == "scatter":

            fig = px.scatter(data,
                             x=x,
                             y=y,
                             title=f"{x} vs {y}")

        elif graph_type == "line":

            fig = px.line(data,
                          x=x,
                          y=y,
                          title=f"{x} vs {y} Trend")

        elif graph_type == "bar":

            grouped = data.groupby(x)[y].mean().reset_index()

            fig = px.bar(grouped,
                         x=x,
                         y=y,
                         title=f"{x} vs {y}")

        elif graph_type == "box":

            fig = px.box(data,
                         x=x,
                         y=y,
                         title=f"{x} vs {y}")

        else:

            fig = px.scatter(data, x=x, y=y)

        return fig

    return None


# =======================
# HEADER DESIGN
# =======================
# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
.main {
    background-color: #f4f6f9;
}
header {
    visibility: hidden;
}
.block-container {
    padding-top: 1rem;
}
.sidebar .sidebar-content {
    background-color: #ffffff;
}
.purple-header {
    background: linear-gradient(90deg, #6a11cb, #8e44ad);
    padding: 15px;
    border-radius: 10px;
    color: white;
    font-size: 22px;
    font-weight: bold;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="purple-header">Interactive Student Performance Tracking App</div>', unsafe_allow_html=True)


role = st.session_state["role"]
if role == "Official":
    tabs = st.tabs([
        "Home",
        "University Dashboard",
        "Student Dashboard",
        "Admin Company Analysis",
        "New Company Drive"
    ])

elif role == "Admin":
    tabs = st.tabs([
        "Home",
        "Admin Company Analysis",
        "New Company Drive"
    ])

elif role == "Student":
    tabs = st.tabs([
        "Home",
        "Student Dashboard"
    ])

with tabs[0]:

    import datetime

    username = st.session_state.get("username", "User")

    # ---------- HEADER ----------
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

    # ================= KPI CARDS =================

    total_students = df["StudentID"].nunique()
    placed_students = df[df["Status"]=="Placed"]["StudentID"].nunique()
    companies = df["Company"].nunique()
    avg_package = round(df[df["Status"]=="Placed"]["Package"].mean(),2)
    placement_rate = round((placed_students/total_students)*100,2)

    c1,c2,c3,c4,c5 = st.columns(5)

    c1.metric(" Students", total_students)
    c2.metric(" Placements", placed_students)
    c3.metric("   Companies", companies)
    c4.metric("   Avg Package", f"{avg_package} LPA")
    c5.metric("   Placement Rate", f"{placement_rate}%")

    st.markdown("---")

   
    # ================= ai =================

    st.subheader("   AI Dataset Analyst")

    question = st.text_input("Ask anything about the dataset")

    if question:

        answer = dataset_ai_engine(question, df)

        st.success(answer)

    st.subheader("   AI Graph Generator")

    graph_query = st.text_input("Ask for any graph")

    if graph_query:

        fig = universal_graph_ai(graph_query, df)

        if fig:

            st.plotly_chart(fig, use_container_width=True)

        else:

            st.warning("AI could not detect attributes in the question.")

    st.markdown("---")
    

# =======================
# UNIVERSITY DASHBOARD
# =======================
with tabs[1]:
    st.markdown("##    Placement Overview Dashboard")

    # ================= YEAR DISTRIBUTION =================

    st.subheader("   Year-wise Student Distribution")

    year_count = df.groupby("Year")["StudentID"].nunique().reset_index()
    year_count.columns = ["Year", "Student Count"]

    fig1 = px.bar(
        year_count,
        x="Year",
        y="Student Count",
        text="Student Count",
        color="Student Count",
        template="plotly_dark"
    )

    st.plotly_chart(fig1, use_container_width=True)

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
    fig1 = px.bar(yearly, x="Year", y="StudentID", template="plotly_dark",
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
        template="plotly_dark"
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
        template="plotly_dark"
    )

    st.plotly_chart(fig6, use_container_width=True)


# =======================
# STUDENT DASHBOARD
# =======================

# =======================
# STUDENT DASHBOARD
# =======================

with tabs[2]:

    st.markdown("##    Student Performance Dashboard")

    search = st.text_input("Search Student (ID or Name)")

    filtered_df = df.copy()

    if search:
        filtered_df = filtered_df[
            filtered_df["StudentID"].astype(str).str.contains(search, na=False) |
            filtered_df["Name"].str.contains(search, case=False, na=False)
        ]

        if filtered_df.empty:
            st.warning("No student found for this search")

    student_list = filtered_df["StudentID"].unique().tolist()

    selected_student = st.selectbox(
        "Select Student ID",
        ["Select Student"] + student_list,
        key="student_selector"
    )

    if selected_student == "Select Student":
        st.info("Please select a student to view the dashboard.")

    else:

        stu_data = df[df["StudentID"].astype(str) == str(selected_student)]

        if stu_data.empty:
            st.warning("No data available for this student.")

        else:

            profile = stu_data.iloc[0]

            total_attempts = len(stu_data)
            placed = len(stu_data[stu_data["Status"] == "Placed"])
            rejected = len(stu_data[stu_data["Status"] == "Rejected"])
            success_ratio = round((placed / total_attempts) * 100, 2)

            # ================= PROFILE =================
            st.markdown("###    Student Profile")

            col1, col2 = st.columns([1,3])

            with col1:
                st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)

            with col2:
                st.markdown(f"""
                **Name:** {profile["Name"]}  
                **Branch:** {profile["Branch"]}  
                **Year:** {profile["Year"]}  
                **CGPA:** {profile["CGPA"]}  
                **Skills:** {profile["Skills"]}
                """)

            # ================= KPI =================
            st.markdown("###    Performance Overview")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("   Total Attempts", total_attempts)
            c2.metric("   Offers", placed)
            c3.metric("   Rejected", rejected)
            c4.metric("   Success %", f"{success_ratio}%")

            # ================= SUCCESS RATIO =================
            st.markdown("###    Success Ratio Analysis")

            fig1 = px.pie(
                names=["Placed","Rejected"],
                values=[placed,rejected],
                hole=0.6,
                color_discrete_sequence=["#4CAF50","#FF4B4B"]
            )

            st.plotly_chart(fig1,use_container_width=True)

            # ================= PLACEMENT HISTORY =================
            st.markdown("###    Placement History")

            fig2 = px.bar(
                stu_data,
                x="Company",
                y="Package",
                color="Status",
                title="Company vs Package",
                barmode="group"
            )

            st.plotly_chart(fig2,use_container_width=True)

            st.dataframe(stu_data[["Company","Package","Status","Placed_Date"]])

            # ================= SGPA TREND =================
            st.markdown("###    Semester-wise CGPA Trend")

            sem_df = pd.DataFrame({
                "Semester":[1,2,3,4,5,6,7,8],
                "SGPA":[
                    profile["SGPA_Sem1"],
                    profile["SGPA_Sem2"],
                    profile["SGPA_Sem3"],
                    profile["SGPA_Sem4"],
                    profile["SGPA_Sem5"],
                    profile["SGPA_Sem6"],
                    profile["SGPA_Sem7"],
                    profile["SGPA_Sem8"]
                ]
            })

            fig = px.line(
                sem_df,
                x="Semester",
                y="SGPA",
                markers=True,
                template="plotly_dark"
            )

            st.plotly_chart(fig,use_container_width=True)

            # ================= SUBJECT MARKS =================

            selected_sem = st.selectbox(
                "Select Semester",
                [1,2,3,4,5,6,7,8],
                key="semester_subject"
            )

            subject_cols = [
                f"Maths_Sem{selected_sem}",
                f"DSA_Sem{selected_sem}",
                f"OS_Sem{selected_sem}",
                f"DBMS_Sem{selected_sem}",
                f"AI_Sem{selected_sem}"
            ]

            subject_df = pd.DataFrame({
                "Subject":["Maths","DSA","OS","DBMS","AI"],
                "Marks":[profile[col] for col in subject_cols]
            })

            fig_sub = px.bar(
                subject_df,
                x="Subject",
                y="Marks",
                text="Marks",
                template="plotly_dark"
            )

            st.plotly_chart(fig_sub,use_container_width=True)

            # ================= BACKLOGS =================
            backlog_df = pd.DataFrame({
                "Semester":[1,2,3,4,5,6,7,8],
                "Backlogs":[
                    profile["Backlogs_Sem1"],
                    profile["Backlogs_Sem2"],
                    profile["Backlogs_Sem3"],
                    profile["Backlogs_Sem4"],
                    profile["Backlogs_Sem5"],
                    profile["Backlogs_Sem6"],
                    profile["Backlogs_Sem7"],
                    profile["Backlogs_Sem8"]
                ]
            })

            fig_back = px.bar(backlog_df,x="Semester",y="Backlogs",template="plotly_dark")

            st.plotly_chart(fig_back,use_container_width=True)

            # ================= ATTENDANCE =================
            attendance_df = pd.DataFrame({
                "Semester":[1,2,3,4,5,6,7,8],
                "Attendance":[
                    profile["Attendance_Sem1"],
                    profile["Attendance_Sem2"],
                    profile["Attendance_Sem3"],
                    profile["Attendance_Sem4"],
                    profile["Attendance_Sem5"],
                    profile["Attendance_Sem6"],
                    profile["Attendance_Sem7"],
                    profile["Attendance_Sem8"]
                ]
            })

            fig_att = px.bar(attendance_df,x="Semester",y="Attendance",template="plotly_dark")

            st.plotly_chart(fig_att,use_container_width=True)

            # ================= PERFORMANCE SCORE =================

            attendance_avg = attendance_df["Attendance"].mean()
            total_backlogs = backlog_df["Backlogs"].sum()

            performance_score = (
                profile["CGPA"]*10 +
                attendance_avg*0.3 +
                profile["Internships"]*5 +
                profile["Hackathons"]*3 +
                profile["Resume_Score"]*0.2 -
                total_backlogs*5
            )

            if performance_score >= 150:
                rating = 5
            elif performance_score >= 130:
                rating = 4
            elif performance_score >= 110:
                rating = 3
            elif performance_score >= 90:
                rating = 2
            else:
                rating = 1

            st.metric("Performance Rating (1  5   )", f"{rating}   ")

            # ================= ACHIEVEMENTS =================

            st.markdown("###    Achievements & Activities")

            a1,a2,a3 = st.columns(3)

            a1.metric("   Hackathons", profile["Hackathons"])
            a1.metric("   Sports", profile["Sports"])

            a2.metric("   Papers Published", profile["Papers"])
            a2.metric("   Conferences", profile["Conferences"])

            a3.metric("   Internships", profile["Internships"])
            a3.metric("   Clubs", profile["Clubs"])

# =======================
# ADMIN COMPANY ANALYSIS
# =======================

with tabs[3]:
    # ============================================================
    # YOUR EXISTING COMPANY ANALYTICS (UNCHANGED)
    # ============================================================

    st.markdown("---")
    st.subheader("   Company-wise Selection Analysis")

    company_year = df[df["Status"]=="Placed"].groupby(["Year","Company"])["StudentID"].nunique().reset_index()

    fig3 = px.bar(company_year, x="Company", y="StudentID", color="Year",
                  template="plotly_dark",
                  title="Company-wise Placements per Year")
    st.plotly_chart(fig3, use_container_width=True)

    year_filter = st.selectbox(
        "Select Year",
        sorted(df["Year"].unique()),
        key="year_filter_company"
    )
    filtered = company_year[company_year["Year"]==year_filter]

    fig4 = px.pie(filtered, names="Company", values="StudentID",
                  title=f"{year_filter} Company Distribution", hole=0.4)
    st.plotly_chart(fig4, use_container_width=True)

    # =====================================================

    st.markdown("##    AI Placement Insights")

    report = generate_narrative_report(df)

    for section, text in report.items():
        st.subheader(section)
        st.write(text)
    # =====================================================
    # ADVANCED COMPANY ANALYTICS DASHBOARD (ADMIN)
    # =====================================================

    st.markdown("##    Advanced Company Analytics")

    placed_df = df[df["Status"]=="Placed"].copy()

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
# 2. COMPANY PACKAGE ANALYSIS
# -----------------------------------------------------
    st.markdown("### 2   Company Package Analysis")

    package_stats = placed_df.groupby("Company")["Package"].agg(
        Highest="max",
        Average="mean",
        Median="median"
    ).reset_index()

    fig = px.bar(
        package_stats,
        x="Company",
        y="Average",
        title="Average Package by Company"
    )
    st.plotly_chart(fig,use_container_width=True)

    fig = px.box(
        placed_df,
        x="Company",
        y="Package",
        title="Salary Distribution by Company"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 3. BRANCH-WISE COMPANY HIRING
    # -----------------------------------------------------
    st.markdown("### 3   Branch-wise Company Preference")

    branch_company = placed_df.groupby(
        ["Branch","Company"]
    )["StudentID"].count().reset_index()

    fig = px.density_heatmap(
        branch_company,
        x="Company",
        y="Branch",
        z="StudentID",
        title="Branch vs Company Hiring"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 4. COMPANY DEMAND ANALYSIS
    # -----------------------------------------------------
    st.markdown("### 4   Company Demand Analysis")

    demand = df.groupby("Company").agg(
        Applicants=("StudentID","count"),
        Selected=("Status",lambda x:(x=="Placed").sum())
    ).reset_index()

    demand["Conversion Rate %"] = round(
        (demand["Selected"]/demand["Applicants"])*100,2
    )

    fig = px.bar(
        demand,
        x="Company",
        y="Applicants",
        color="Conversion Rate %",
        title="Applicants vs Selection Rate"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 5. COMPANY DIFFICULTY INDEX
    # -----------------------------------------------------
    st.markdown("### 5   Company Difficulty Index")

    difficulty = demand.copy()
    difficulty["Difficulty Score"] = round(
        difficulty["Applicants"]/difficulty["Selected"].replace(0,1),2
    )

    fig = px.bar(
        difficulty,
        x="Company",
        y="Difficulty Score",
        title="Company Difficulty Score"
    )
    st.plotly_chart(fig,use_container_width=True)


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
    # 7. OFFER ACCEPTANCE ANALYSIS
    # -----------------------------------------------------
    st.markdown("### 7   Offer Acceptance Analysis")

    offer_dist = df["Status"].value_counts().reset_index()
    offer_dist.columns = ["Status","Count"]

    fig = px.pie(
        offer_dist,
        names="Status",
        values="Count",
        hole=0.4,
        title="Offer Acceptance Distribution"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 8. INTERNSHIP TO PPO CONVERSION
    # -----------------------------------------------------
    st.markdown("### 8   Internship to PPO Conversion")

    if "JobType" in df.columns:
        ppo = df["JobType"].value_counts().reset_index()
        ppo.columns = ["Type","Count"]

        fig = px.bar(
            ppo,
            x="Type",
            y="Count",
            title="Internship vs Full-time Hiring"
        )
        st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 9. COMPANY RETENTION ANALYSIS
    # -----------------------------------------------------
    st.markdown("### 9   Company Retention")

    retention = df.groupby("Company")["Year"].nunique().reset_index()
    retention.columns = ["Company","Years Visited"]

    fig = px.bar(
        retention,
        x="Company",
        y="Years Visited",
        title="Company Retention (Years Visiting Campus)"
    )
    st.plotly_chart(fig,use_container_width=True)


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
    # 11. INTERVIEW MODE ANALYSIS
    # -----------------------------------------------------
    st.markdown("### 1  1   Interview Mode Analysis")

    if "InterviewMode" in df.columns:

        mode = df["InterviewMode"].value_counts().reset_index()
        mode.columns = ["Mode","Count"]

        fig = px.pie(
            mode,
            names="Mode",
            values="Count",
            hole=0.4,
            title="Interview Mode Distribution"
        )
        st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 12. HIRING SPEED ANALYSIS
    # -----------------------------------------------------
    st.markdown("### 1  2   Hiring Speed Analysis")

    if "Placed_Date" in df.columns:

        speed = df.groupby("Company")["Placed_Date"].min().reset_index()

        fig = px.histogram(
            speed,
            x="Placed_Date",
            title="Hiring Timeline Distribution"
        )
        st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 13. COMPANY QUALITY SCORE
    # -----------------------------------------------------
    st.markdown("### 1  3   Company Quality Score")

    quality = package_stats.merge(company_perf,on="Company")

    quality["Score"] = (
        quality["Average"]*0.4 +
        quality["Selection Rate %"]*0.3 +
        50*0.3
    )

    fig = px.bar(
        quality,
        x="Company",
        y="Score",
        title="Company Quality Score"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 14. PLACEMENT COVERAGE
    # -----------------------------------------------------
    st.markdown("### 1  4   Placement Coverage")

    coverage = placed_df["Company"].value_counts().reset_index()
    coverage.columns = ["Company","Students"]

    fig = px.pie(
        coverage,
        names="Company",
        values="Students",
        title="Placement Share by Company"
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

# ============================================================
# ADMIN COMPANY DRIVE MANAGEMENT INTERFACE
# ============================================================
with tabs[4]:
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

            st.success("   Company Drive Registered Successfully")
            st.json(company_data)

=======
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
# ================================
# SESSION INIT
# ================================

if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None

# ================================
# SECRET KEY
# ================================
SECRET_KEY = "PLACEMENT_INTELLIGENCE_APEX_ENTERPRISE_SECURITY_2026"


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

        st.markdown('<div class="login-box">', unsafe_allow_html=True)

        st.title("   Placement Intelligence Apex")
        st.caption("AI Powered Placement Analytics Portal")

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


# =======================
# LOAD CSV DATA
# =======================

@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv("PLACEMENT_INTELLIGENCE_MASTER_FINAL_LARGE.csv")
    df["Placed_Date"] = pd.to_datetime(df["Placed_Date"], errors="coerce")
    return df

df = load_data()

# ==========================================================
# AI NARRATIVE INTERPRETATION ENGINE
# ==========================================================

def generate_narrative_report(df):

    placed = df[df["Status"] == "Placed"].copy()

    report = {}

    # ---------------- Hiring Performance ----------------
    company_hires = placed["Company"].value_counts()
    top_company = company_hires.idxmax()
    top_count = company_hires.max()

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
# UNIVERSAL DATA ANALYSIS ENGINE
# ============================================================

def dataset_ai_engine(question, df):

    q = question.lower()

    data = df.copy()

    detected_columns = detect_columns(q, df)

    year = detect_year(q)

    if year and "Year" in df.columns:

        data = data[data["Year"] == year]


    # ========================================================
    # MOST / HIGHEST
    # ========================================================

    if "most" in q or "highest" in q or "maximum" in q:

        if "company" in q:

            placed = data[data["Status"] == "Placed"]

            counts = placed["Company"].value_counts()

            company = counts.idxmax()

            count = counts.max()

            return f"{company} hired the most students ({count})."


        if "package" in q:

            row = data.loc[data["Package"].idxmax()]

            return f"""
Highest Package Analysis

Student : {row['Name']}

Company : {row['Company']}

Package :   {row['Package']} LPA
"""


        if "cgpa" in q:

            row = data.loc[data["CGPA"].idxmax()]

            return f"{row['Name']} has the highest CGPA of {row['CGPA']}."


        if "branch" in q:

            placed = data[data["Status"] == "Placed"]

            branch = placed["Branch"].value_counts().idxmax()

            return f"{branch} branch has the highest placements."


    # ========================================================
    # TOP N ANALYSIS
    # ========================================================

    if "top" in q:

        number = re.search(r"\d+", q)

        n = 5

        if number:
            n = int(number.group())

        if "package" in q:

            top = data.sort_values("Package", ascending=False).head(n)

            result = f"Top {n} Highest Packages\n\n"

            for _, r in top.iterrows():

                result += f"{r['Name']} - {r['Company']} -   {r['Package']} LPA\n"

            return result


        if "cgpa" in q:

            top = data.sort_values("CGPA", ascending=False).head(n)

            result = f"Top {n} Students by CGPA\n\n"

            for _, r in top.iterrows():

                result += f"{r['Name']} - {r['CGPA']}\n"

            return result


    # ========================================================
    # COUNT QUERIES
    # ========================================================

    if "how many" in q or "count" in q:

        if "students" in q:

            return f"Total Students : {data['StudentID'].nunique()}"


        if "placed" in q:

            placed = data[data["Status"] == "Placed"]

            return f"Placed Students : {placed['StudentID'].nunique()}"


        if "company" in q:

            return f"Total Companies : {data['Company'].nunique()}"


    # ========================================================
    # AVERAGE ANALYSIS
    # ========================================================

    if "average" in q or "mean" in q:

        if "package" in q:

            avg = data["Package"].mean()

            return f"Average Package :   {round(avg,2)} LPA"


        if "cgpa" in q:

            avg = data["CGPA"].mean()

            return f"Average CGPA : {round(avg,2)}"


    # ========================================================
    # GENERAL DATA EXPLORATION
    # ========================================================

    if detected_columns:

        col = detected_columns[0]

        if data[col].dtype in ["int64","float64"]:

            return f"""
Statistics for {col}

Mean : {round(data[col].mean(),2)}

Max : {data[col].max()}

Min : {data[col].min()}
"""

        else:

            return f"""
Top values for {col}

{data[col].value_counts().head(5)}
"""


    return "I analyzed the dataset but could not fully interpret the question."

# ==========================================================
# UNIVERSAL GRAPH GENERATOR FOR ALL DATASET ATTRIBUTES
# ==========================================================

import plotly.express as px
import re

def universal_graph_ai(question, df):

    q = question.lower()

    columns = df.columns.tolist()

    detected = []

    # Detect columns mentioned in question
    for col in columns:

        col_name = col.lower()

        if col_name in q:
            detected.append(col)

    # Detect graph type
    graph_type = "scatter"

    if "bar" in q:
        graph_type = "bar"

    elif "line" in q or "trend" in q:
        graph_type = "line"

    elif "hist" in q or "distribution" in q:
        graph_type = "hist"

    elif "box" in q:
        graph_type = "box"

    # Detect year filter
    year_match = re.search(r"\b20\d{2}\b", q)

    data = df.copy()

    if year_match and "Year" in df.columns:

        year = int(year_match.group())

        data = data[data["Year"] == year]

    # =========================
    # ONE COLUMN GRAPH
    # =========================

    if len(detected) == 1:

        col = detected[0]

        if graph_type == "hist":

            fig = px.histogram(data, x=col,
                               title=f"{col} Distribution")

        elif graph_type == "box":

            fig = px.box(data, y=col,
                         title=f"{col} Spread")

        else:

            counts = data[col].value_counts().reset_index()

            fig = px.bar(counts,
                         x="index",
                         y=col,
                         title=f"{col} Frequency")

        return fig

    # =========================
    # TWO COLUMN GRAPH
    # =========================

    if len(detected) >= 2:

        x = detected[0]
        y = detected[1]

        if graph_type == "scatter":

            fig = px.scatter(data,
                             x=x,
                             y=y,
                             title=f"{x} vs {y}")

        elif graph_type == "line":

            fig = px.line(data,
                          x=x,
                          y=y,
                          title=f"{x} vs {y} Trend")

        elif graph_type == "bar":

            grouped = data.groupby(x)[y].mean().reset_index()

            fig = px.bar(grouped,
                         x=x,
                         y=y,
                         title=f"{x} vs {y}")

        elif graph_type == "box":

            fig = px.box(data,
                         x=x,
                         y=y,
                         title=f"{x} vs {y}")

        else:

            fig = px.scatter(data, x=x, y=y)

        return fig

    return None


# =======================
# HEADER DESIGN
# =======================
# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
.main {
    background-color: #f4f6f9;
}
header {
    visibility: hidden;
}
.block-container {
    padding-top: 1rem;
}
.sidebar .sidebar-content {
    background-color: #ffffff;
}
.purple-header {
    background: linear-gradient(90deg, #6a11cb, #8e44ad);
    padding: 15px;
    border-radius: 10px;
    color: white;
    font-size: 22px;
    font-weight: bold;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="purple-header">Interactive Student Performance Tracking App</div>', unsafe_allow_html=True)


role = st.session_state["role"]
if role == "Official":
    tabs = st.tabs([
        "Home",
        "University Dashboard",
        "Student Dashboard",
        "Admin Company Analysis",
        "New Company Drive"
    ])

elif role == "Admin":
    tabs = st.tabs([
        "Home",
        "Admin Company Analysis",
        "New Company Drive"
    ])

elif role == "Student":
    tabs = st.tabs([
        "Home",
        "Student Dashboard"
    ])

with tabs[0]:

    import datetime

    username = st.session_state.get("username", "User")

    # ---------- HEADER ----------
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

    # ================= KPI CARDS =================

    total_students = df["StudentID"].nunique()
    placed_students = df[df["Status"]=="Placed"]["StudentID"].nunique()
    companies = df["Company"].nunique()
    avg_package = round(df[df["Status"]=="Placed"]["Package"].mean(),2)
    placement_rate = round((placed_students/total_students)*100,2)

    c1,c2,c3,c4,c5 = st.columns(5)

    c1.metric(" Students", total_students)
    c2.metric(" Placements", placed_students)
    c3.metric("   Companies", companies)
    c4.metric("   Avg Package", f"{avg_package} LPA")
    c5.metric("   Placement Rate", f"{placement_rate}%")

    st.markdown("---")

   
    # ================= ai =================

    st.subheader("   AI Dataset Analyst")

    question = st.text_input("Ask anything about the dataset")

    if question:

        answer = dataset_ai_engine(question, df)

        st.success(answer)

    st.subheader("   AI Graph Generator")

    graph_query = st.text_input("Ask for any graph")

    if graph_query:

        fig = universal_graph_ai(graph_query, df)

        if fig:

            st.plotly_chart(fig, use_container_width=True)

        else:

            st.warning("AI could not detect attributes in the question.")

    st.markdown("---")
    

# =======================
# UNIVERSITY DASHBOARD
# =======================
with tabs[1]:
    st.markdown("##    Placement Overview Dashboard")

    # ================= YEAR DISTRIBUTION =================

    st.subheader("   Year-wise Student Distribution")

    year_count = df.groupby("Year")["StudentID"].nunique().reset_index()
    year_count.columns = ["Year", "Student Count"]

    fig1 = px.bar(
        year_count,
        x="Year",
        y="Student Count",
        text="Student Count",
        color="Student Count",
        template="plotly_dark"
    )

    st.plotly_chart(fig1, use_container_width=True)

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
    fig1 = px.bar(yearly, x="Year", y="StudentID", template="plotly_dark",
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
        template="plotly_dark"
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
        template="plotly_dark"
    )

    st.plotly_chart(fig6, use_container_width=True)


# =======================
# STUDENT DASHBOARD
# =======================

# =======================
# STUDENT DASHBOARD
# =======================

with tabs[2]:

    st.markdown("##    Student Performance Dashboard")

    search = st.text_input("Search Student (ID or Name)")

    filtered_df = df.copy()

    if search:
        filtered_df = filtered_df[
            filtered_df["StudentID"].astype(str).str.contains(search, na=False) |
            filtered_df["Name"].str.contains(search, case=False, na=False)
        ]

        if filtered_df.empty:
            st.warning("No student found for this search")

    student_list = filtered_df["StudentID"].unique().tolist()

    selected_student = st.selectbox(
        "Select Student ID",
        ["Select Student"] + student_list,
        key="student_selector"
    )

    if selected_student == "Select Student":
        st.info("Please select a student to view the dashboard.")

    else:

        stu_data = df[df["StudentID"].astype(str) == str(selected_student)]

        if stu_data.empty:
            st.warning("No data available for this student.")

        else:

            profile = stu_data.iloc[0]

            total_attempts = len(stu_data)
            placed = len(stu_data[stu_data["Status"] == "Placed"])
            rejected = len(stu_data[stu_data["Status"] == "Rejected"])
            success_ratio = round((placed / total_attempts) * 100, 2)

            # ================= PROFILE =================
            st.markdown("###    Student Profile")

            col1, col2 = st.columns([1,3])

            with col1:
                st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)

            with col2:
                st.markdown(f"""
                **Name:** {profile["Name"]}  
                **Branch:** {profile["Branch"]}  
                **Year:** {profile["Year"]}  
                **CGPA:** {profile["CGPA"]}  
                **Skills:** {profile["Skills"]}
                """)

            # ================= KPI =================
            st.markdown("###    Performance Overview")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("   Total Attempts", total_attempts)
            c2.metric("   Offers", placed)
            c3.metric("   Rejected", rejected)
            c4.metric("   Success %", f"{success_ratio}%")

            # ================= SUCCESS RATIO =================
            st.markdown("###    Success Ratio Analysis")

            fig1 = px.pie(
                names=["Placed","Rejected"],
                values=[placed,rejected],
                hole=0.6,
                color_discrete_sequence=["#4CAF50","#FF4B4B"]
            )

            st.plotly_chart(fig1,use_container_width=True)

            # ================= PLACEMENT HISTORY =================
            st.markdown("###    Placement History")

            fig2 = px.bar(
                stu_data,
                x="Company",
                y="Package",
                color="Status",
                title="Company vs Package",
                barmode="group"
            )

            st.plotly_chart(fig2,use_container_width=True)

            st.dataframe(stu_data[["Company","Package","Status","Placed_Date"]])

            # ================= SGPA TREND =================
            st.markdown("###    Semester-wise CGPA Trend")

            sem_df = pd.DataFrame({
                "Semester":[1,2,3,4,5,6,7,8],
                "SGPA":[
                    profile["SGPA_Sem1"],
                    profile["SGPA_Sem2"],
                    profile["SGPA_Sem3"],
                    profile["SGPA_Sem4"],
                    profile["SGPA_Sem5"],
                    profile["SGPA_Sem6"],
                    profile["SGPA_Sem7"],
                    profile["SGPA_Sem8"]
                ]
            })

            fig = px.line(
                sem_df,
                x="Semester",
                y="SGPA",
                markers=True,
                template="plotly_dark"
            )

            st.plotly_chart(fig,use_container_width=True)

            # ================= SUBJECT MARKS =================

            selected_sem = st.selectbox(
                "Select Semester",
                [1,2,3,4,5,6,7,8],
                key="semester_subject"
            )

            subject_cols = [
                f"Maths_Sem{selected_sem}",
                f"DSA_Sem{selected_sem}",
                f"OS_Sem{selected_sem}",
                f"DBMS_Sem{selected_sem}",
                f"AI_Sem{selected_sem}"
            ]

            subject_df = pd.DataFrame({
                "Subject":["Maths","DSA","OS","DBMS","AI"],
                "Marks":[profile[col] for col in subject_cols]
            })

            fig_sub = px.bar(
                subject_df,
                x="Subject",
                y="Marks",
                text="Marks",
                template="plotly_dark"
            )

            st.plotly_chart(fig_sub,use_container_width=True)

            # ================= BACKLOGS =================
            backlog_df = pd.DataFrame({
                "Semester":[1,2,3,4,5,6,7,8],
                "Backlogs":[
                    profile["Backlogs_Sem1"],
                    profile["Backlogs_Sem2"],
                    profile["Backlogs_Sem3"],
                    profile["Backlogs_Sem4"],
                    profile["Backlogs_Sem5"],
                    profile["Backlogs_Sem6"],
                    profile["Backlogs_Sem7"],
                    profile["Backlogs_Sem8"]
                ]
            })

            fig_back = px.bar(backlog_df,x="Semester",y="Backlogs",template="plotly_dark")

            st.plotly_chart(fig_back,use_container_width=True)

            # ================= ATTENDANCE =================
            attendance_df = pd.DataFrame({
                "Semester":[1,2,3,4,5,6,7,8],
                "Attendance":[
                    profile["Attendance_Sem1"],
                    profile["Attendance_Sem2"],
                    profile["Attendance_Sem3"],
                    profile["Attendance_Sem4"],
                    profile["Attendance_Sem5"],
                    profile["Attendance_Sem6"],
                    profile["Attendance_Sem7"],
                    profile["Attendance_Sem8"]
                ]
            })

            fig_att = px.bar(attendance_df,x="Semester",y="Attendance",template="plotly_dark")

            st.plotly_chart(fig_att,use_container_width=True)

            # ================= PERFORMANCE SCORE =================

            attendance_avg = attendance_df["Attendance"].mean()
            total_backlogs = backlog_df["Backlogs"].sum()

            performance_score = (
                profile["CGPA"]*10 +
                attendance_avg*0.3 +
                profile["Internships"]*5 +
                profile["Hackathons"]*3 +
                profile["Resume_Score"]*0.2 -
                total_backlogs*5
            )

            if performance_score >= 150:
                rating = 5
            elif performance_score >= 130:
                rating = 4
            elif performance_score >= 110:
                rating = 3
            elif performance_score >= 90:
                rating = 2
            else:
                rating = 1

            st.metric("Performance Rating (1  5   )", f"{rating}   ")

            # ================= ACHIEVEMENTS =================

            st.markdown("###    Achievements & Activities")

            a1,a2,a3 = st.columns(3)

            a1.metric("   Hackathons", profile["Hackathons"])
            a1.metric("   Sports", profile["Sports"])

            a2.metric("   Papers Published", profile["Papers"])
            a2.metric("   Conferences", profile["Conferences"])

            a3.metric("   Internships", profile["Internships"])
            a3.metric("   Clubs", profile["Clubs"])

# =======================
# ADMIN COMPANY ANALYSIS
# =======================

with tabs[3]:
    # ============================================================
    # YOUR EXISTING COMPANY ANALYTICS (UNCHANGED)
    # ============================================================

    st.markdown("---")
    st.subheader("   Company-wise Selection Analysis")

    company_year = df[df["Status"]=="Placed"].groupby(["Year","Company"])["StudentID"].nunique().reset_index()

    fig3 = px.bar(company_year, x="Company", y="StudentID", color="Year",
                  template="plotly_dark",
                  title="Company-wise Placements per Year")
    st.plotly_chart(fig3, use_container_width=True)

    year_filter = st.selectbox(
        "Select Year",
        sorted(df["Year"].unique()),
        key="year_filter_company"
    )
    filtered = company_year[company_year["Year"]==year_filter]

    fig4 = px.pie(filtered, names="Company", values="StudentID",
                  title=f"{year_filter} Company Distribution", hole=0.4)
    st.plotly_chart(fig4, use_container_width=True)

    # =====================================================

    st.markdown("##    AI Placement Insights")

    report = generate_narrative_report(df)

    for section, text in report.items():
        st.subheader(section)
        st.write(text)
    # =====================================================
    # ADVANCED COMPANY ANALYTICS DASHBOARD (ADMIN)
    # =====================================================

    st.markdown("##    Advanced Company Analytics")

    placed_df = df[df["Status"]=="Placed"].copy()

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
# 2. COMPANY PACKAGE ANALYSIS
# -----------------------------------------------------
    st.markdown("### 2   Company Package Analysis")

    package_stats = placed_df.groupby("Company")["Package"].agg(
        Highest="max",
        Average="mean",
        Median="median"
    ).reset_index()

    fig = px.bar(
        package_stats,
        x="Company",
        y="Average",
        title="Average Package by Company"
    )
    st.plotly_chart(fig,use_container_width=True)

    fig = px.box(
        placed_df,
        x="Company",
        y="Package",
        title="Salary Distribution by Company"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 3. BRANCH-WISE COMPANY HIRING
    # -----------------------------------------------------
    st.markdown("### 3   Branch-wise Company Preference")

    branch_company = placed_df.groupby(
        ["Branch","Company"]
    )["StudentID"].count().reset_index()

    fig = px.density_heatmap(
        branch_company,
        x="Company",
        y="Branch",
        z="StudentID",
        title="Branch vs Company Hiring"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 4. COMPANY DEMAND ANALYSIS
    # -----------------------------------------------------
    st.markdown("### 4   Company Demand Analysis")

    demand = df.groupby("Company").agg(
        Applicants=("StudentID","count"),
        Selected=("Status",lambda x:(x=="Placed").sum())
    ).reset_index()

    demand["Conversion Rate %"] = round(
        (demand["Selected"]/demand["Applicants"])*100,2
    )

    fig = px.bar(
        demand,
        x="Company",
        y="Applicants",
        color="Conversion Rate %",
        title="Applicants vs Selection Rate"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 5. COMPANY DIFFICULTY INDEX
    # -----------------------------------------------------
    st.markdown("### 5   Company Difficulty Index")

    difficulty = demand.copy()
    difficulty["Difficulty Score"] = round(
        difficulty["Applicants"]/difficulty["Selected"].replace(0,1),2
    )

    fig = px.bar(
        difficulty,
        x="Company",
        y="Difficulty Score",
        title="Company Difficulty Score"
    )
    st.plotly_chart(fig,use_container_width=True)


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
    # 7. OFFER ACCEPTANCE ANALYSIS
    # -----------------------------------------------------
    st.markdown("### 7   Offer Acceptance Analysis")

    offer_dist = df["Status"].value_counts().reset_index()
    offer_dist.columns = ["Status","Count"]

    fig = px.pie(
        offer_dist,
        names="Status",
        values="Count",
        hole=0.4,
        title="Offer Acceptance Distribution"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 8. INTERNSHIP TO PPO CONVERSION
    # -----------------------------------------------------
    st.markdown("### 8   Internship to PPO Conversion")

    if "JobType" in df.columns:
        ppo = df["JobType"].value_counts().reset_index()
        ppo.columns = ["Type","Count"]

        fig = px.bar(
            ppo,
            x="Type",
            y="Count",
            title="Internship vs Full-time Hiring"
        )
        st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 9. COMPANY RETENTION ANALYSIS
    # -----------------------------------------------------
    st.markdown("### 9   Company Retention")

    retention = df.groupby("Company")["Year"].nunique().reset_index()
    retention.columns = ["Company","Years Visited"]

    fig = px.bar(
        retention,
        x="Company",
        y="Years Visited",
        title="Company Retention (Years Visiting Campus)"
    )
    st.plotly_chart(fig,use_container_width=True)


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
    # 11. INTERVIEW MODE ANALYSIS
    # -----------------------------------------------------
    st.markdown("### 1  1   Interview Mode Analysis")

    if "InterviewMode" in df.columns:

        mode = df["InterviewMode"].value_counts().reset_index()
        mode.columns = ["Mode","Count"]

        fig = px.pie(
            mode,
            names="Mode",
            values="Count",
            hole=0.4,
            title="Interview Mode Distribution"
        )
        st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 12. HIRING SPEED ANALYSIS
    # -----------------------------------------------------
    st.markdown("### 1  2   Hiring Speed Analysis")

    if "Placed_Date" in df.columns:

        speed = df.groupby("Company")["Placed_Date"].min().reset_index()

        fig = px.histogram(
            speed,
            x="Placed_Date",
            title="Hiring Timeline Distribution"
        )
        st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 13. COMPANY QUALITY SCORE
    # -----------------------------------------------------
    st.markdown("### 1  3   Company Quality Score")

    quality = package_stats.merge(company_perf,on="Company")

    quality["Score"] = (
        quality["Average"]*0.4 +
        quality["Selection Rate %"]*0.3 +
        50*0.3
    )

    fig = px.bar(
        quality,
        x="Company",
        y="Score",
        title="Company Quality Score"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 14. PLACEMENT COVERAGE
    # -----------------------------------------------------
    st.markdown("### 1  4   Placement Coverage")

    coverage = placed_df["Company"].value_counts().reset_index()
    coverage.columns = ["Company","Students"]

    fig = px.pie(
        coverage,
        names="Company",
        values="Students",
        title="Placement Share by Company"
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

# ============================================================
# ADMIN COMPANY DRIVE MANAGEMENT INTERFACE
# ============================================================
with tabs[4]:
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

            st.success("   Company Drive Registered Successfully")
            st.json(company_data)
