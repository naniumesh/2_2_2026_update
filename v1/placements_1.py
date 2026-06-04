import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Placement Intelligence Apex", layout="wide", page_icon="🎓")

# =======================
# LOAD CSV DATA
# =======================

@st.cache_data
def load_data():
    df = pd.read_csv("placement_10_years_india_realistic.csv")
    df["Placed_Date"] = pd.to_datetime(df["Placed_Date"], errors="coerce")
    return df

df = load_data()

# =======================
# HEADER DESIGN
# =======================

st.markdown("""
<style>
.main { background: radial-gradient(circle at center, #050a0f 0%, #010409 100%); color: #e6edf3; }
h1 { text-align:center; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>PLACEMENT INTELLIGENCE APEX</h1>", unsafe_allow_html=True)

# =======================
# MAIN KPIs
# =======================

total_students = df["StudentID"].nunique()
offers = len(df[df["Status"]=="Placed"])
placement_rate = round((offers/total_students)*100,2)
avg_package = round(df[df["Status"]=="Placed"]["Package"].mean(),2)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Students (10Y)", total_students)
c2.metric("Total Placements", offers)
c3.metric("Placement Rate %", placement_rate)
c4.metric("Average Package ₹", avg_package)

tabs = st.tabs(["University Overview","Student Dashboard","Admin Company Analysis"])

# =======================
# UNIVERSITY OVERVIEW
# =======================

with tabs[0]:
    st.subheader("Year-wise Placement Performance")
    yearly = df[df["Status"]=="Placed"].groupby("Year")["StudentID"].nunique().reset_index()
    fig1 = px.bar(yearly, x="Year", y="StudentID", template="plotly_dark",
                  title="Year-wise Unique Placements")
    st.plotly_chart(fig1, use_container_width=True)

    branch_perf = df[df["Status"]=="Placed"].groupby("Branch")["StudentID"].nunique().reset_index()
    fig2 = px.pie(branch_perf, names="Branch", values="StudentID", hole=0.5,
                  title="Branch Contribution (10 Years)")
    st.plotly_chart(fig2, use_container_width=True)

# =======================
# STUDENT DASHBOARD
# =======================

with tabs[1]:
    st.subheader("Student Search & Performance Analytics")
    
    student_list = df["StudentID"].unique()
    selected_student = st.selectbox("Select Student ID", student_list)
    
    stu_data = df[df["StudentID"]==selected_student]
    profile = stu_data.iloc[0]
    
    total_attempts = len(stu_data)
    placed = len(stu_data[stu_data["Status"]=="Placed"])
    rejected = len(stu_data[stu_data["Status"]=="Rejected"])
    success_ratio = round((placed/total_attempts)*100,2) if total_attempts > 0 else 0
    
    st.write("### Student Profile")
    st.write({
        "Name": profile["Name"],
        "Branch": profile["Branch"],
        "Year": profile["Year"],
        "CGPA": profile["CGPA"],
        "Skills": profile["Skills"]
    })
    
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Attempts", total_attempts)
    s2.metric("Offers", placed)
    s3.metric("Rejected", rejected)
    s4.metric("Success Ratio %", success_ratio)
    
    st.write("### Placement History")
    st.dataframe(stu_data[["Company","Package","Status","Placed_Date"]])
    
    # AI Clustering
    st.write("### AI Performance Cluster")
    scaler = StandardScaler()
    features = df[["CGPA","Package"]].fillna(0)
    X = scaler.fit_transform(features)
    kmeans = KMeans(n_clusters=4, random_state=42)
    df["Cluster"] = kmeans.fit_predict(X)
    cluster_group = df[df["StudentID"]==selected_student]["Cluster"].iloc[0]
    st.success(f"Cluster Group: {cluster_group}")

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
