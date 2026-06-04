import pandas as pd
import numpy as np
import random
from faker import Faker

fake = Faker("en_IN")

# ---------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------

YEARS = list(range(2016, 2026))

STUDENTS_PER_BRANCH = 120

COMPANY_COUNT = 500

BRANCHES = [
"CSE",
"CSE – Data Science",
"CSE – Cloud Technology & Information Security",
"CSE – Mobile Applications & Cloud Technology",
"CSE – Artificial Intelligence & Machine Learning",
"CSE – Artificial Intelligence & Data Engineering",
"CSE – Blockchain Technology",
"CSE – Cyber Physical Systems",
"CSE – AI Driven DevOps",
"Computer Science & Business Systems",
"CSE – Internet of Things",
"Computer Engineering – Software Engineering",
"CSE – Artificial Intelligence",
"Mechanical Engineering",
"Mechanical – Mechatronics",
"Mechanical – Robotics",
"Civil Engineering",
"Civil – Environmental Geotechnology",
"Civil – Construction Technology",
"ECE",
"ECE – VLSI Design",
"ECE – Robotics",
"EEE",
"EEE – Electric Vehicles"
]

SKILLS = [
"Python","Java","C++","SQL","Machine Learning","Deep Learning",
"Cloud Computing","AWS","DevOps","Docker","Kubernetes",
"Cybersecurity","Blockchain","IoT","Data Science",
"React","NodeJS","TensorFlow","PyTorch","Linux"
]

# ---------------------------------------------------
# COMPANIES
# ---------------------------------------------------

companies = []

for i in range(COMPANY_COUNT):

    companies.append({
        "CompanyID": i+1,
        "Company": fake.company(),
        "Industry": random.choice(["IT","Finance","Consulting","Manufacturing"]),
        "Headquarters": fake.city(),
        "Employees": random.randint(100,100000),
        "Founded": random.randint(1980,2020),
        "Tier": random.choice(["Tier1","Tier2","Tier3"]),
        "Difficulty_Index": round(np.random.uniform(1,10),2)
    })

companies_df = pd.DataFrame(companies)
companies_df.to_csv("companies_master.csv",index=False)

company_list = companies_df["Company"].tolist()

# =====================================
# BRANCH SUBJECT STRUCTURE
# =====================================

BRANCH_SUBJECTS = {

"CSE":[
["Maths1","Physics","Programming_C","Engineering_Graphics"],
["Maths2","Data_Structures","Digital_Logic","Electronics"],
["OOP","Computer_Organization","Discrete_Maths","DBMS"],
["Operating_Systems","Computer_Networks","Software_Engineering","Web_Tech"],
["Artificial_Intelligence","Machine_Learning","Cloud_Computing","Compiler"],
["Big_Data","Cyber_Security","DevOps","Data_Engineering"],
["Blockchain","IoT","Deep_Learning","Distributed_Systems"],
["Major_Project","Internship","Seminar","Capstone"]
],

"ECE":[
["Maths1","Physics","Basic_Electronics","Programming_C"],
["Maths2","Data_Structures","Digital_Logic","Electronics"],
["Signals_Systems","Analog_Electronics","Network_Theory","Devices"],
["Digital_Electronics","Microprocessors","Control_Systems","EMT"],
["Communication_Systems","VLSI","Embedded_Systems","DSP"],
["Wireless_Comm","DSP_Advanced","IoT_Systems","FPGA"],
["Robotics","Satellite_Comm","Advanced_VLSI","Image_Processing"],
["Major_Project","Internship","Seminar","Capstone"]
],

"Civil":[
["Maths1","Physics","Engineering_Graphics","Programming_C"],
["Maths2","Engineering_Mechanics","Environmental_Science","Materials"],
["Strength_of_Materials","Surveying","Fluid_Mechanics","Geology"],
["Structural_Analysis","Geotechnical","Transportation","Hydrology"],
["Concrete_Tech","Environmental_Engineering","Foundation","Construction_Mgmt"],
["Water_Resources","Structural_Design","Urban_Planning","GIS"],
["Earthquake_Engineering","Advanced_Structures","Bridge_Design","Project_Mgmt"],
["Major_Project","Internship","Seminar","Capstone"]
],

"Mechanical":[
["Maths1","Physics","Engineering_Graphics","Programming_C"],
["Maths2","Engineering_Mechanics","Materials","Workshop"],
["Thermodynamics","Manufacturing","Strength_of_Materials","Kinematics"],
["Fluid_Mechanics","Machine_Design","Heat_Transfer","Metrology"],
["IC_Engines","CAD_CAM","Robotics","Dynamics"],
["Mechatronics","Industrial_Engineering","Automation","FEM"],
["Advanced_Manufacturing","Product_Design","Energy_Systems","AI_in_Mech"],
["Major_Project","Internship","Seminar","Capstone"]
]

}

# ---------------------------------------------------
# STUDENTS
# ---------------------------------------------------

students = []
sid = 1

for year in YEARS:

    for branch in BRANCHES:

        for i in range(STUDENTS_PER_BRANCH):

            skills = ",".join(random.sample(SKILLS,5))

            students.append({

                "StudentID": sid,
                "Name": fake.name(),
                "Gender": random.choice(["Male","Female"]),
                "DOB": fake.date_of_birth(minimum_age=18, maximum_age=23),
                "Email": fake.email(),
                "Phone": fake.phone_number(),
                "Branch": branch,
                "Year": year,
                "CGPA": round(np.random.uniform(6.0,9.8),2),

                "Skills": skills,

                "Hackathons": random.randint(0,5),
                "Papers": random.randint(0,3),
                "Conferences": random.randint(0,2),
                "Sports": random.randint(0,3),
                "Clubs": random.randint(0,4),
                "Internships": random.randint(0,2),

                "Resume_Score": random.randint(50,100),
                "GitHub_Score": random.randint(0,100),
                "LeetCode_Rating": random.randint(800,2200),

                "Placement_Probability": round(np.random.uniform(0.3,0.95),2),

                "Father": fake.name(),
                "Mother": fake.name(),
                "Address": fake.address()

            })

            sid += 1

students_df = pd.DataFrame(students)
students_df.to_csv("placement_master_10yr_full_dataset.csv",index=False)

# ---------------------------------------------------
# ACADEMIC HISTORY
# ---------------------------------------------------

academic_rows = []

for _, row in students_df.iterrows():

    branch = row["Branch"]

    # detect branch category
    branch_key = "CSE"

    if "ECE" in branch:
        branch_key = "ECE"
    elif "Civil" in branch:
        branch_key = "Civil"
    elif "Mechanical" in branch:
        branch_key = "Mechanical"

    record = {
        "StudentID": row["StudentID"],
        "Year": row["Year"]
    }

    # SGPA / Attendance / Backlogs
    for i in range(1,9):

        record[f"SGPA_Sem{i}"] = round(np.random.uniform(6.5,9.5),2)
        record[f"Attendance_Sem{i}"] = random.randint(65,95)
        record[f"Backlogs_Sem{i}"] = random.randint(0,2)

    # Branch specific subjects
    for sem in range(1,9):

        subjects = BRANCH_SUBJECTS[branch_key][sem-1]

        for subject in subjects:

            record[f"{subject}_Sem{sem}"] = random.randint(55,100)

    academic_rows.append(record)

academic_df = pd.DataFrame(academic_rows)

academic_df.to_csv("academic_history_10years.csv",index=False)
# ---------------------------------------------------
# PLACEMENT HISTORY
# ---------------------------------------------------

placements = []

for _,row in students_df.iterrows():

    attempts = random.randint(3,8)

    for a in range(attempts):

        company = random.choice(company_list)

        status = random.choices(
            ["Placed","Rejected"],
            weights=[0.35,0.65]
        )[0]

        placements.append({

            "StudentID": row["StudentID"],
            "Year": row["Year"],
            "Company": company,
            "package" : np.random.uniform(3,18),
            if random.random() < 0.05:
                package = np.random.uniform(18,40)
            "Status": status,
            "InterviewMode": random.choice(["Online","Offline"]),
            "JobType": random.choice(["Full Time","Internship","Internship + PPO"]),
            "Interview_Rounds": random.randint(2,5),
            "Placed_Date": fake.date_between(start_date='-10y',end_date='today')

        })

placement_df = pd.DataFrame(placements)
placement_df.to_csv("placement_history_10years.csv",index=False)

# ---------------------------------------------------
# MIS DRIVES
# ---------------------------------------------------

drives = []

for year in YEARS:

    visiting = random.sample(company_list, random.randint(100,180))

    for c in visiting:

        drives.append({

            "Year": year,
            "Company": c,
            "Drive_ID": fake.uuid4(),
            "Drive_Mode": random.choice(["Online","Offline"]),
            "Eligible_Branches": ",".join(random.sample(BRANCHES,5)),
            "Students_Eligible": random.randint(200,2000),
            "Students_Applied": random.randint(100,1500),
            "Students_Shortlisted": random.randint(50,500),
            "Students_Selected": random.randint(5,200)

        })

drives_df = pd.DataFrame(drives)
drives_df.to_csv("mis_drives_10years.csv",index=False)

print("ENTERPRISE DATASET CREATED SUCCESSFULLY")