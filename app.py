import streamlit as st

st.set_page_config(page_title="NetSage AI", page_icon="🔍", layout="wide")

st.title("🔍 NetSage AI")
st.subheader("AI Troubleshooting Assistant for Cisco-Style Lab Networks")

st.markdown("""
Welcome to **NetSage AI** — an evidence-driven troubleshooting assistant that pairs 
structured AI diagnosis with deterministic rule-based checks and **mandatory human review**.

---

### 📄 Pages

- **🩺 Review** — Review AI diagnoses case-by-case. Mark as Accepted, Edited, or Rejected.
- **📊 Dashboard** — View dataset coverage, AI vs. human agreement, and Responsible AI logs.

---

### How It Works

1. A network troubleshooting case (symptom + show-command output) is submitted.
2. The **deterministic rule checker** flags mechanical config errors (duplicate IPs, gateway mismatch, etc.).
3. The **AI diagnosis engine** (Groq / Llama 3.3 70B) analyzes the case and returns a structured JSON diagnosis.
4. A **human reviewer** examines both outputs and marks the diagnosis as Accepted, Edited, or Rejected.
5. All decisions are logged for **auditability** and the **Responsible AI record**.

> ⚠️ **Core Safety Rule:** No AI diagnosis is considered final until a human reviewer approves it.
""")

# Show quick stats
import sqlite3
import db

db.init_db()

conn = sqlite3.connect(db.DB_FILE)
try:
    total_cases = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
    total_diagnoses = conn.execute("SELECT COUNT(*) FROM diagnoses").fetchone()[0]
    total_reviews = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    total_corrections = conn.execute("SELECT COUNT(*) FROM responsible_ai_log").fetchone()[0]
except:
    total_cases = total_diagnoses = total_reviews = total_corrections = 0
conn.close()

col1, col2, col3, col4 = st.columns(4)
col1.metric("📁 Cases", total_cases)
col2.metric("🤖 Diagnoses", total_diagnoses)
col3.metric("👤 Reviews", total_reviews)
col4.metric("📝 AI Corrections", total_corrections)
