import pandas as pd
import numpy as np
import random
from faker import Faker

fake = Faker("en_IN")

YEARS = list(range(2016, 2026))

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

COMPANY_NAMES = [fake.company() for _ in range(350)]

# --------------------------------------------------
# COMPANY MASTER
# --------------------------------------------------

companies = []

for i,c in enumerate(COMPANY_NAMES):

    companies.append({
        "CompanyID": i+1,
        "Company": c,
        "Industry": random.choice(["IT","Finance","Consulting","Manufacturing"]),
        "Headquarters": fake.city(),
        "Employees": random.randint(100,100000),
        "Founded": random.randint(1980,2020),
        "Tier": random.choice(["Tier1","Tier2","Tier3"])
    })

companies_df = pd.DataFrame(companies)
companies_df.to_csv("companies_master.csv",index=False)


# --------------------------------------------------
# STUDENT MASTER
# --------------------------------------------------

students = []
sid = 1

for year in YEARS:

    for branch in BRANCHES:

        for i in range(120):

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

                "Father": fake.name(),
                "Mother": fake.name(),
                "Address": fake.address(),

                "Resume_Score": random.randint(50,100),

                "GitHub_Score": random.randint(0,100),
                "LeetCode_Rating": random.randint(800,2200),

                "Placement_Probability": round(np.random.uniform(0.3,0.95),2)

            })

            sid += 1

students_df = pd.DataFrame(students)
students_df.to_csv("placement_master_10yr_full_dataset.csv",index=False)


# --------------------------------------------------
# ACADEMIC HISTORY
# --------------------------------------------------

academic_rows = []

for _,row in students_df.iterrows():

    for year in YEARS:

        academic_rows.append({

            "StudentID": row["StudentID"],
            "Year": year,

            **{f"SGPA_Sem{i}": round(np.random.uniform(6.5,9.5),2) for i in range(1,9)},
            **{f"Attendance_Sem{i}": random.randint(65,95) for i in range(1,9)},
            **{f"Backlogs_Sem{i}": random.randint(0,2) for i in range(1,9)},

            **{f"Maths_Sem{i}": random.randint(50,100) for i in range(1,9)},
            **{f"DSA_Sem{i}": random.randint(50,100) for i in range(1,9)},
            **{f"OS_Sem{i}": random.randint(50,100) for i in range(1,9)},
            **{f"DBMS_Sem{i}": random.randint(50,100) for i in range(1,9)},
            **{f"AI_Sem{i}": random.randint(50,100) for i in range(1,9)}

        })

academic_df = pd.DataFrame(academic_rows)
academic_df.to_csv("academic_history_10years.csv",index=False)


# --------------------------------------------------
# PLACEMENT HISTORY
# --------------------------------------------------

placement_rows = []

for _,row in students_df.iterrows():

    attempts = random.randint(3,8)

    for a in range(attempts):

        company = random.choice(COMPANY_NAMES)

        status = random.choices(
            ["Placed","Rejected"],
            weights=[0.35,0.65]
        )[0]

        placement_rows.append({

            "StudentID": row["StudentID"],
            "Year": row["Year"],
            "Company": company,
            "Package": round(np.random.uniform(3,35),2),
            "Status": status,
            "InterviewMode": random.choice(["Online","Offline"]),
            "JobType": random.choice(["Full Time","Internship","Internship + PPO"]),
            "Interview_Rounds": random.randint(2,5),
            "Placed_Date": fake.date_between(start_date='-10y',end_date='today')
        })

placement_df = pd.DataFrame(placement_rows)
placement_df.to_csv("placement_history_10years.csv",index=False)


# --------------------------------------------------
# MIS DRIVES
# --------------------------------------------------

drives = []

for year in YEARS:

    companies_year = random.sample(COMPANY_NAMES, random.randint(80,140))

    for c in companies_year:

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

print("ENTERPRISE DATASET GENERATED SUCCESSFULLY")