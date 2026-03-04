pip install plotly
import streamlit as st
import pandas as pd
import numpy as np
import requests
from pathlib import Path
from datetime import datetime
import plotly.express as px
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# ---------------------------------------
# PAGE CONFIG
# ---------------------------------------

st.set_page_config(
    page_title="MPDTE AI Counselling Assistant",
    page_icon="🎓",
    layout="wide"
)

# ---------------------------------------
# LOAD DATA
# ---------------------------------------

BASE = Path(__file__).parent
DATA_FILE = BASE / "data/mpdte_2025.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(DATA_FILE)

    df["OPENING JEE COMMON RANK"] = pd.to_numeric(df["OPENING JEE COMMON RANK"])
    df["CLOSING JEE COMMON RANK"] = pd.to_numeric(df["CLOSING JEE COMMON RANK"])

    df["BRANCH"] = df["BRANCH"].str.upper().str.strip()
    df["INSTITUTE TYPE"] = df["INSTITUTE TYPE"].str.upper()

    return df

df = load_data()

# ---------------------------------------
# PRIORITY SYSTEM
# ---------------------------------------

INSTITUTE_PRIORITY = {
    "GOVERNMENT AIDED":1,
    "GOVERNMENT AUTONOMOUS":2,
    "PRIVATE":3,
    "SELF FINANCING":4
}

BRANCH_PRIORITY = {
    "CSE":1,
    "CSEAI":2,
    "CSEDS":3,
    "IT":4,
    "AIML":5,
    "ECE":6,
    "EE":7,
    "MECH":8,
    "CIVIL":9
}

# ---------------------------------------
# HEADER
# ---------------------------------------

st.title("🎓 MPDTE AI Counselling Assistant")

col1,col2,col3 = st.columns(3)

col1.metric("Institutes", df["INSTITUTE NAME"].nunique())
col2.metric("Branches", df["BRANCH"].nunique())
col3.metric("Total Options", len(df))

# ---------------------------------------
# USER INPUT
# ---------------------------------------

st.subheader("Candidate Details")

c1,c2 = st.columns(2)

with c1:
    name = st.text_input("Full Name")
    rank = st.number_input("JEE CRL Rank", min_value=1)

with c2:
    category = st.selectbox("Category",["UR","OBC","SC","ST"])
    domicile = st.selectbox("MP Domicile",["YES","NO"])

# ---------------------------------------
# USER ANALYTICS
# ---------------------------------------

def log_user():

    try:
        ip = requests.get("https://api64.ipify.org?format=json").json()["ip"]
    except:
        ip = "unknown"

    data = {
        "name":name,
        "rank":rank,
        "category":category,
        "domicile":domicile,
        "ip":ip,
        "time":datetime.now()
    }

    log = pd.DataFrame([data])

    log.to_csv(
        "logs/users.csv",
        mode="a",
        header=not Path("logs/users.csv").exists(),
        index=False
    )

# ---------------------------------------
# AI FILTER ENGINE
# ---------------------------------------

def get_eligible(df, rank):

    margin = 20000

    eligible = df[
        (df["OPENING JEE COMMON RANK"] <= rank) &
        (df["CLOSING JEE COMMON RANK"] >= rank-margin)
    ]

    return eligible

# ---------------------------------------
# DREAM / SAFE CLASSIFICATION
# ---------------------------------------

def classify(row, rank):

    close = row["CLOSING JEE COMMON RANK"]

    if rank <= close:
        return "SAFE"

    elif rank <= close + 20000:
        return "MODERATE"

    else:
        return "DREAM"

# ---------------------------------------
# CHOICE ENGINE
# ---------------------------------------

def generate_choices(df, rank):

    df["InstScore"] = df["INSTITUTE TYPE"].map(INSTITUTE_PRIORITY).fillna(5)
    df["BranchScore"] = df["BRANCH"].map(BRANCH_PRIORITY).fillna(50)

    df["ChoiceScore"] = df["InstScore"]*100 + df["BranchScore"]

    df["Prediction"] = df.apply(lambda r: classify(r,rank),axis=1)

    df = df.sort_values("ChoiceScore")

    df["Choice"] = range(1,len(df)+1)

    return df.head(150)

# ---------------------------------------
# GENERATE RESULT
# ---------------------------------------

if st.button("🚀 Generate AI Counselling List"):

    log_user()

    eligible = get_eligible(df,rank)

    choices = generate_choices(eligible,rank)

    st.success(f"{len(choices)} Recommended Choices Generated")

    st.dataframe(
        choices[[
            "Choice",
            "INSTITUTE NAME",
            "BRANCH",
            "Prediction",
            "OPENING JEE COMMON RANK",
            "CLOSING JEE COMMON RANK"
        ]],
        use_container_width=True
    )

# ---------------------------------------
# RANK VS COLLEGE GRAPH
# ---------------------------------------

    fig = px.scatter(
        choices,
        x="CLOSING JEE COMMON RANK",
        y="INSTITUTE NAME",
        color="Prediction",
        title="Rank vs College Probability"
    )

    st.plotly_chart(fig,use_container_width=True)

# ---------------------------------------
# PDF REPORT
# ---------------------------------------

    def generate_pdf(df):

        buffer = BytesIO()

        styles = getSampleStyleSheet()

        story = []

        story.append(Paragraph(
            f"MPDTE Counselling Report - {name}",
            styles["Title"]
        ))

        table_data = [["Choice","College","Branch","Prediction"]]

        for _,r in df.iterrows():

            table_data.append([
                r["Choice"],
                r["INSTITUTE NAME"],
                r["BRANCH"],
                r["Prediction"]
            ])

        table = Table(table_data)

        story.append(table)

        pdf = SimpleDocTemplate(buffer,pagesize=A4)

        pdf.build(story)

        return buffer

    pdf = generate_pdf(choices)

    st.download_button(
        "📄 Download Counselling Report",
        pdf,
        file_name="mpdte_counselling_report.pdf"
    )

