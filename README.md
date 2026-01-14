# 🎓 MPDTE B.Tech Counselling Assistant

A **real-world eligibility-based counselling tool** for MPDTE B.Tech admissions using **previous year cutoff data (2025)**.

This system helps students explore **eligible colleges and branches** based on:
- JEE Common Rank (CRL)
- Category & reservation rules
- Institute type preference
- Branch priority (as per counselling behavior)

---

## ✨ Features

- 📊 Eligibility check using official cutoff ranges
- 🏫 Institute type priority (Aided → Autonomous → Private → SFI)
- 🎯 Branch priority logic (CSE → Core → Allied)
- 🧑‍🎓 Category logic (UR includes EWS)
- 📥 Download eligible list as PDF
- 🛠 Debug mode for transparency
- 💻 Clean, modern Streamlit UI

---

## 🧠 Logic Philosophy

This tool does **NOT** predict allotment.  
It provides **eligibility-based guidance**, similar to how real counselling decisions are made.

---

## 🗂 Data Source

- MPDTE Previous Year Counselling Data (2025)
- Stored internally as Excel (`mpdte_2025.xlsx`)

---

## 🚀 How to Run Locally

```bash
git clone https://github.com/dipanshudhage/MPDTE-B.Tech-Counselling-Assistant.git
cd mpdte_predictor
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
streamlit run app.py
