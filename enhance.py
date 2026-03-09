import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Placement Intelligence Apex", layout="wide", page_icon="🎓")
# 🔐 User database (Add as many as you want)
USERS = {
    "admin": {"password": "apex2026", "role": "Admin"},
    "naga": {"password": "naash123", "role": "Admin"},
}

def login():

    st.title("🔐 Placement Intelligence Apex Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    login_button = st.button("Login")

    if login_button:
        if username in USERS and USERS[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = USERS[username]["role"]
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid Username or Password ❌")

# Initialize session
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# =======================
# LOAD CSV DATA
# =======================

@st.cache_data
def load_data():
    df = pd.read_csv("PLACEMENT_INTELLIGENCE_MASTER_FINAL_LARGE.csv")
    df["Placed_Date"] = pd.to_datetime(df["Placed_Date"], errors="coerce")
    return df

df = load_data()

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


tabs = st.tabs(["Home ","Student Dashboard","Admin Company Analysis"])

#=======================
# home
#=======================
with tabs[0]:
    st.markdown("## 📊 Placement Overview Dashboard")

    # ---------------- KPI CALCULATIONS ----------------
    total_students = df["StudentID"].nunique()
    offers = len(df[df["Status"]=="Placed"])
    placement_rate = round((offers/total_students)*100,2)
    avg_package = round(df[df["Status"]=="Placed"]["Package"].mean(),2)

    # ---------------- KPI CARDS ----------------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🎓 Total Students", total_students)
    c2.metric("🏢 Total Offers", offers)
    c3.metric("📈 Placement Rate (%)", placement_rate)
    c4.metric("💰 Avg Package (LPA)", avg_package)

    st.markdown("---")

    # ---------------- YEAR-WISE STUDENT COUNT ----------------
    st.markdown("### 📅 Year-wise Student Distribution")

    year_count = df.groupby("Year")["StudentID"].nunique().reset_index()
    year_count.columns = ["Year", "Student Count"]

    fig1 = px.bar(
        year_count,
        x="Year",
        y="Student Count",
        text="Student Count",
        color="Student Count"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ---------------- YEAR-WISE PLACEMENT RATE ----------------
    st.markdown("### 📊 Year-wise Placement Rate")

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
    st.markdown("### 💰 Year-wise Average Package")

    year_package = df[df["Status"]=="Placed"].groupby("Year")["Package"].mean().reset_index()
    year_package["Package"] = round(year_package["Package"],2)

    fig3 = px.area(
        year_package,
        x="Year",
        y="Package"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ---------------- STATUS DISTRIBUTION ----------------
    st.markdown("### 🎯 Overall Placement Distribution")

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
    #-----------------Branch Contribution
    branch_perf = df[df["Status"]=="Placed"].groupby("Branch")["StudentID"].nunique().reset_index()
    fig2 = px.pie(branch_perf, names="Branch", values="StudentID", hole=0.5,
                  title="Branch Contribution (10 Years)")
    st.plotly_chart(fig2, use_container_width=True)


# =======================
# STUDENT DASHBOARD
# =======================

with tabs[1]:
    st.markdown("## 🎓 Student Performance Dashboard")
    search = st.text_input("Search Student (ID or Name)")
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df["StudentID"].astype(str).str.contains(search) |   
        filtered_df["Name"].str.contains(search, case=False)]
        

    student_list = filtered_df["StudentID"].unique()
    if len(student_list) == 0:
        st.warning("No student found")
        st.stop()
    selected_student = st.selectbox("Select Student ID", student_list)


    stu_data = df[df["StudentID"] == selected_student]
    profile = stu_data.iloc[0]

    total_attempts = len(stu_data)
    placed = len(stu_data[stu_data["Status"] == "Placed"])
    rejected = len(stu_data[stu_data["Status"] == "Rejected"])
    success_ratio = round((placed / total_attempts) * 100, 2) if total_attempts > 0 else 0

    # ================= PROFILE SECTION =================
    st.markdown("### 👤 Student Profile")

    col1, col2 = st.columns([1, 3])

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

    # ================= KPI CARDS =================
    st.markdown("### 📊 Performance Overview")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("📌 Total Attempts", total_attempts)
    c2.metric("🏢 Offers", placed)
    c3.metric("❌ Rejected", rejected)
    c4.metric("📈 Success %", f"{success_ratio}%")

    # ================= DONUT CHART =================
    st.markdown("### 📈 Success Ratio Analysis")

    fig1 = px.pie(
        names=["Placed", "Rejected"],
        values=[placed, rejected],
        hole=0.6,
        color_discrete_sequence=["#4CAF50", "#FF4B4B"]
    )
    fig1.update_layout(showlegend=True)
    st.plotly_chart(fig1, use_container_width=True)

    # ================= PLACEMENT HISTORY =================
    st.markdown("### 🏢 Placement History")

    fig2 = px.bar(
        stu_data,
        x="Company",
        y="Package",
        color="Status",
        title="Company vs Package",
        barmode="group"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(stu_data[["Company", "Package", "Status", "Placed_Date"]])


    # ---------------- SEMESTER CGPA TREND ----------------
    st.markdown("### 📈 Semester-wise CGPA Trend")
    sem_data = {
    "Semester": [1,2,3,4,5,6,7,8],
    "SGPA": [
        profile["SGPA_Sem1"],
        profile["SGPA_Sem2"],
        profile["SGPA_Sem3"],
        profile["SGPA_Sem4"],
        profile["SGPA_Sem5"],
        profile["SGPA_Sem6"],
        profile["SGPA_Sem7"],
        profile["SGPA_Sem8"]
        ]
    }

    sem_df = pd.DataFrame(sem_data)

    fig = px.line(
        sem_df,
        x="Semester",
        y="SGPA",
        markers=True,
        title="Semester-wise SGPA Progress",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------------- SUBJECTS VS MARKS ----------------
    selected_sem = st.selectbox("Select Semester", [1,2,3,4,5,6,7,8])

    subject_cols = [
        f"Maths_Sem{selected_sem}",
        f"DSA_Sem{selected_sem}",
        f"OS_Sem{selected_sem}",
        f"DBMS_Sem{selected_sem}",
        f"AI_Sem{selected_sem}"
    ]

    subject_names = ["Maths", "DSA", "OS", "DBMS", "AI"]

    subject_data = {
        "Subject": subject_names,
        "Marks": [profile[col] for col in subject_cols]
    }

    sub_df = pd.DataFrame(subject_data)

    fig_sub = px.bar(
        sub_df,
        x="Subject",
        y="Marks",
        text="Marks",
        title=f"Subject Marks - Semester {selected_sem}",
        template="plotly_dark"
    )

    st.plotly_chart(fig_sub, use_container_width=True)

    # ---------------- BACKLOG ANALYSIS ----------------
    backlog_data = {
    "Semester": [1,2,3,4,5,6,7,8],
    "Backlogs": [
        profile["Backlogs_Sem1"],
        profile["Backlogs_Sem2"],
        profile["Backlogs_Sem3"],
        profile["Backlogs_Sem4"],
        profile["Backlogs_Sem5"],
        profile["Backlogs_Sem6"],
        profile["Backlogs_Sem7"],
        profile["Backlogs_Sem8"]
        ]
    }
    backlog_df = pd.DataFrame(backlog_data)

    fig_back = px.bar(
        backlog_df,
        x="Semester",
        y="Backlogs",
        text="Backlogs",
        template="plotly_dark"
    )

    st.plotly_chart(fig_back, use_container_width=True)

    # ---------------- ATTENDANCE ----------------
    attendance_data = {
    "Semester": [1,2,3,4,5,6,7,8],
    "Attendance": [
        profile["Attendance_Sem1"],
        profile["Attendance_Sem2"],
        profile["Attendance_Sem3"],
        profile["Attendance_Sem4"],
        profile["Attendance_Sem5"],
        profile["Attendance_Sem6"],
        profile["Attendance_Sem7"],
        profile["Attendance_Sem8"]
        ]
    }

    attendance_df = pd.DataFrame(attendance_data)

    fig_att = px.bar(
        attendance_df,
        x="Semester",
        y="Attendance",
        text="Attendance",
        template="plotly_dark"
    )

    st.plotly_chart(fig_att, use_container_width=True)

    # ---------------- STUDENT RANKING ----------------

    # Average attendance
    attendance_avg = sum([
        profile["Attendance_Sem1"],
        profile["Attendance_Sem2"],
        profile["Attendance_Sem3"],
        profile["Attendance_Sem4"],
        profile["Attendance_Sem5"],
        profile["Attendance_Sem6"],
        profile["Attendance_Sem7"],
        profile["Attendance_Sem8"]
    ]) / 8

    # Total backlogs
    total_backlogs = sum([
        profile["Backlogs_Sem1"],
        profile["Backlogs_Sem2"],
        profile["Backlogs_Sem3"],
        profile["Backlogs_Sem4"],
        profile["Backlogs_Sem5"],
        profile["Backlogs_Sem6"],
        profile["Backlogs_Sem7"],
        profile["Backlogs_Sem8"]
    ])

    # Performance score formula
    performance_score = (
        profile["CGPA"] * 10
        + attendance_avg * 0.3
        + profile["Internships"] * 5
        + profile["Hackathons"] * 3
        + profile["Resume_Score"] * 0.2
        - total_backlogs * 5
    )

    # Convert score to 1–5 rating
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

    st.metric("Performance Rating (1–5 ⭐)", f"{rating} ⭐")

    # ---------------- SUBJECT PROGRESS RADAR ----------------
    # Select semester
    selected_sem = st.selectbox("Select Semester for Subject Analysis", [1,2,3,4,5,6,7,8])

    # Build subject column names dynamically
    subject_columns = {
        "Maths": f"Maths_Sem{selected_sem}",
        "DSA": f"DSA_Sem{selected_sem}",
        "OS": f"OS_Sem{selected_sem}",
        "DBMS": f"DBMS_Sem{selected_sem}",
        "AI": f"AI_Sem{selected_sem}"
    }

    # Create DataFrame
    subject_marks = pd.DataFrame({
        "Subject": list(subject_columns.keys()),
        "Marks": [profile[col] for col in subject_columns.values()]
    })

    # Bar chart
    fig_sub = px.bar(
        subject_marks,
        x="Subject",
        y="Marks",
        text="Marks",
        title=f"Subject Marks - Semester {selected_sem}",
        template="plotly_dark"
    )
    st.plotly_chart(fig_sub, use_container_width=True, key=f"subject_bar_{selected_sem}")

    # Radar chart
    fig_radar = px.line_polar(
        subject_marks,
        r="Marks",
        theta="Subject",
        line_close=True,
        title=f"Performance Radar - Semester {selected_sem}",
        template="plotly_dark"
    )   

    st.plotly_chart(fig_radar, use_container_width=True, key=f"subject_radar_{selected_sem}")

    # ---------------- ACHIEVEMENTS ----------------
    st.markdown("### 🌟 Achievements & Activities")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🏆 Hackathons", profile["Hackathons"])
        st.metric("⚽ Sports", profile["Sports"])

    with col2:
        st.metric("📄 Papers Published", profile["Papers"])
        st.metric("🎤 Conferences", profile["Conferences"])

    with col3:
        st.metric("💼 Internships", profile["Internships"])
        st.metric("👥 Clubs", profile["Clubs"])

    # ================= AI CLUSTERING =================
    st.markdown("### AI Performance Cluster")

    scaler = StandardScaler()
    features = df[["CGPA", "Package"]].fillna(0)
    X = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=4, random_state=42)
    df["Cluster"] = kmeans.fit_predict(X)

    cluster_group = df[df["StudentID"] == selected_student]["Cluster"].iloc[0]

    st.success(f" Student belongs to Cluster Group: {cluster_group}")

# =======================
# ADMIN COMPANY ANALYSIS
# =======================

with tabs[2]:
    st.subheader("Company-wise Selection Analysis")
    
    company_year = df[df["Status"]=="Placed"].groupby(["Year","Company"])["StudentID"].nunique().reset_index()
    
    fig3 = px.bar(company_year, x="Company", y="StudentID", color="Year",
                  template="plotly_dark",
                  title="Company-wise Placements per Year")
    st.plotly_chart(fig3, use_container_width=True)
    
    year_filter = st.selectbox("Select Year", sorted(df["Year"].unique()))
    filtered = company_year[company_year["Year"]==year_filter]
    
    fig4 = px.pie(filtered, names="Company", values="StudentID",
                  title=f"{year_filter} Company Distribution", hole=0.4)
    st.plotly_chart(fig4, use_container_width=True)

st.caption("Placement Intelligence Apex | 10-Year Enterprise System | NAGA ASHOK 2026")

