import streamlit as st
import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# =====================================================
# PAGE CONFIG + THEME
# =====================================================
st.set_page_config(page_title="MPDTE Counselling Assistant", layout="wide")

st.markdown("""
<style>
body { background-color:#f8fafc; }
.metric-card {
    background:white; padding:1rem; border-radius:14px;
    box-shadow:0 4px 12px rgba(0,0,0,0.08); text-align:center;
}
.big-btn button {
    padding:0.9rem !important;
    font-size:18px !important;
    border-radius:14px !important;
    font-weight:700;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# CONSTANTS
# =====================================================
INSTITUTE_PRIORITY = [
    "GOVERNMENT AIDED",
    "GOVERNMENT AUTONOMOUS",
    "PRIVATE",
    "SELF FINANCING"
]

INSTITUTE_MAP = {
    "AIDED": "GOVERNMENT AIDED",
    "GOVT": "GOVERNMENT AUTONOMOUS",
    "PRIVATE": "PRIVATE",
    "S.F.I": "SELF FINANCING"
}

BRANCH_PRIORITY = [
    "CSE","CSEAI","CSEIML","CSEDS","AIML","AIAIDS","AIADS","DS",
    "CSEAIADS","CSEBC","CSECS","CSIT","IT","ITAIAR","CYSEC",
    "CSBS","CSD","CST","CSEIOT","CSEITCS","CSERC","ECS","INOT",
    "IP","CMPS","MAC","LG","EACE","ECACT",
    "ELECTRONICS AND TELECOMMUNICATIONS","ET","ELEX","ELECT ELEX",
    "EC","EE","EEVDT","EI","EL","EV","ARE","AIR","AGRITECH",
    "AG","AGE","AUTO","MECH","MINING","MTENG",
    "CE","CENG","CEWCA","BM","BT","BEIL","CHEM","PCT","FTS","EAPE"
]

CLASS_MAP = {
    "ALL": "ALL",
    "Nil": "X",
    "Physically Handicapped": "H",
    "Sainik": "S",
    "Freedom Fighter": "FF",
    "Technical Stream": "TS"
}

# =====================================================
# LOAD DATA (EXCEL)
# =====================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "mpdte_2025.xlsx"

@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        st.error("❌ data/mpdte_2025.xlsx not found")
        st.stop()

    df = pd.read_excel(DATA_FILE)

    df["OPENING JEE COMMON RANK"] = pd.to_numeric(df["OPENING JEE COMMON RANK"], errors="coerce")
    df["CLOSING JEE COMMON RANK"] = pd.to_numeric(df["CLOSING JEE COMMON RANK"], errors="coerce")

    df["INSTITUTE TYPE"] = (
        df["INSTITUTE TYPE"].astype(str).str.upper().str.strip().replace(INSTITUTE_MAP)
    )

    df["BRANCH"] = df["BRANCH"].astype(str).str.upper().str.strip()

    # 🔑 Normalize ALLOTTED CATEGORY
    df["ALLOTTED CATEGORY"] = (
        df["ALLOTTED CATEGORY"]
        .astype(str)
        .str.upper()
        .str.replace(" ", "")
        .str.replace("-", "/")
    )

    # Normalize domicile
    df["DOMICILE"] = (
        df["DOMICILE"]
        .astype(str)
        .str.upper()
        .replace({"D": "Y", "YES": "Y", "NO": "N"})
    )

    df.dropna(subset=[
        "INSTITUTE NAME",
        "INSTITUTE TYPE",
        "BRANCH",
        "OPENING JEE COMMON RANK",
        "CLOSING JEE COMMON RANK",
        "ALLOTTED CATEGORY"
    ], inplace=True)

    return df

df_base = load_data()

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<h1 style="text-align:center;">🎓 MPDTE B.Tech Counselling Assistant</h1>
<p style="text-align:center; font-size:16px; color:#475569;">
Eligibility-based college & branch explorer (MPDTE 2025)
</p>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.markdown(f"<div class='metric-card'><h3>{df_base['INSTITUTE NAME'].nunique()}</h3><p>Institutes</p></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='metric-card'><h3>{df_base['BRANCH'].nunique()}</h3><p>Branches</p></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='metric-card'><h3>{len(df_base)}</h3><p>Total Options</p></div>", unsafe_allow_html=True)

# =====================================================
# USER INPUT
# =====================================================
st.markdown("## 🧑‍🎓 Candidate Details")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Full Name")
    crl = st.number_input("JEE Common Rank (CRL)", min_value=1)
with col2:
    domicile = st.selectbox("MP Domicile", ["ALL","YES","NO"])
    category = st.selectbox("Category", ["ALL","UR","OBC","SC","ST"])

st.markdown("## 🏷️ Reservation & Preference")

col3, col4 = st.columns(2)
with col3:
    cls_ui = st.selectbox("Class", list(CLASS_MAP.keys()))
with col4:
    institute_type = st.selectbox("Institute Type", ["ALL"] + INSTITUTE_PRIORITY)

debug = st.checkbox("🛠 Debug mode")

cls = CLASS_MAP[cls_ui]

st.markdown("## 🚀 Generate Result")
run = st.button("🔍 View Eligible Colleges", use_container_width=True)

if not run:
    st.stop()

# =====================================================
# CORE LOGIC WITH DEBUG COUNTERS
# =====================================================
debug_count = {
    "total": len(df_base),
    "rank": 0,
    "category": 0,
    "class": 0,
    "op": 0,
    "domicile": 0,
    "institute": 0
}

eligible = []

for _, r in df_base.iterrows():
    debug_count["rank"] += 1
    if not (r["OPENING JEE COMMON RANK"] <= crl <= r["CLOSING JEE COMMON RANK"]):
        continue

    debug_count["category"] += 1
    allot = r["ALLOTTED CATEGORY"]

    if category != "ALL":
        if category == "UR":
            if not (allot.startswith("UR") or allot.startswith("EWS")):
                continue
        elif not allot.startswith(category):
            continue

    debug_count["class"] += 1
    if cls != "ALL" and f"/{cls}/" not in allot:
        if "/X/" not in allot:
            continue

    debug_count["op"] += 1
    if "/OP" not in allot:
        continue

    debug_count["domicile"] += 1
    if domicile == "YES" and r["DOMICILE"] == "N":
        continue
    if domicile == "NO" and r["DOMICILE"] != "X":
        continue

    debug_count["institute"] += 1
    if institute_type != "ALL" and r["INSTITUTE TYPE"] != institute_type:
        continue

    eligible.append(r)

df = pd.DataFrame(eligible)

if debug:
    st.subheader("🛠 Debug Breakdown")
    st.json(debug_count)

if df.empty:
    st.warning("No eligible colleges found for the given inputs.")
    st.stop()

# =====================================================
# SORTING
# =====================================================
df["InstPriority"] = df["INSTITUTE TYPE"].apply(
    lambda x: INSTITUTE_PRIORITY.index(x) if x in INSTITUTE_PRIORITY else 99
)
df["BranchPriority"] = df["BRANCH"].apply(
    lambda x: BRANCH_PRIORITY.index(x) if x in BRANCH_PRIORITY else 999
)

if institute_type == "ALL":
    df = df.sort_values(["InstPriority","BranchPriority","OPENING JEE COMMON RANK"])
else:
    df = df.sort_values(["BranchPriority","OPENING JEE COMMON RANK"])

# =====================================================
# RESULTS
# =====================================================
st.markdown("## 🏫 Eligible Colleges & Branches")

for college, g in df.groupby("INSTITUTE NAME"):
    with st.expander(f"🏫 {college} ({g.iloc[0]['INSTITUTE TYPE']})"):
        st.dataframe(
            g[[
                "BRANCH",
                "ALLOTTED CATEGORY",
                "OPENING JEE COMMON RANK",
                "CLOSING JEE COMMON RANK"
            ]].reset_index(drop=True),
            use_container_width=True
        )

# =====================================================
# PDF DOWNLOAD
# =====================================================
def generate_pdf(df, name, crl):
    file = f"{name}_MPDTE_Eligible_List.pdf"
    c = canvas.Canvas(file, pagesize=A4)
    y = 800
    c.setFont("Helvetica-Bold",14)
    c.drawString(40,y,"MPDTE Eligible College List")
    y -= 25
    c.setFont("Helvetica",10)
    c.drawString(40,y,f"Name: {name} | CRL: {crl}")
    y -= 20

    for i,r in df.iterrows():
        c.drawString(
            40,y,
            f"{i+1}. {r['INSTITUTE NAME']} | {r['BRANCH']} | "
            f"{r['ALLOTTED CATEGORY']} | OR:{r['OPENING JEE COMMON RANK']} | "
            f"CR:{r['CLOSING JEE COMMON RANK']}"
        )
        y -= 14
        if y < 50:
            c.showPage()
            y = 800

    c.save()
    return file

st.markdown("## 📥 Download")
if st.button("📄 Download Eligible List (PDF)", use_container_width=True):
    path = generate_pdf(df, name, crl)
    with open(path, "rb") as f:
        st.download_button("⬇️ Click to Download", f, file_name=path, use_container_width=True)

st.warning("⚠️ Eligibility based on previous-year MPDTE data. Actual allotment may vary.")
