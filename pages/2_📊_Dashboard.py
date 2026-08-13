import streamlit as st
import sqlite3
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import db

st.title("📊 NetSage AI Metrics Dashboard")

conn = sqlite3.connect(db.DB_FILE)

# 1. Dataset Coverage
st.header("Dataset Coverage")
cases_df = pd.read_sql_query("SELECT concept_tag, severity FROM cases", conn)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Cases by Concept")
    concept_counts = cases_df['concept_tag'].value_counts()
    st.bar_chart(concept_counts)
    
with col2:
    st.subheader("Cases by Severity")
    severity_counts = cases_df['severity'].value_counts()
    st.bar_chart(severity_counts)

st.divider()

# 2. AI vs Human Agreement
st.header("AI vs Human Agreement")
reviews_df = pd.read_sql_query("SELECT decision FROM reviews", conn)
if not reviews_df.empty:
    decision_counts = reviews_df['decision'].value_counts()
    st.bar_chart(decision_counts)
else:
    st.write("No reviews submitted yet.")

st.divider()

# 3. Responsible AI Log
st.header("Responsible AI Log (Corrected Cases)")
log_df = pd.read_sql_query("SELECT case_id, original_ai_output, corrected_diagnosis, rationale, logged_at FROM responsible_ai_log", conn)

if not log_df.empty:
    st.markdown(f"**Total Corrections: {len(log_df)}** (Target: at least 5)")
    st.dataframe(log_df, use_container_width=True)
else:
    st.write("No AI corrections logged yet.")

conn.close()

# Generate responsible_ai_log.md dynamically
if st.button("Export Responsible AI Log to Markdown"):
    if not log_df.empty:
        with open('responsible_ai_log.md', 'w', encoding='utf-8') as f:
            f.write("# Responsible AI Log\n\n")
            f.write("This log documents cases where the AI's initial diagnosis was materially wrong and corrected by a human reviewer.\n\n")
            for idx, row in log_df.iterrows():
                f.write(f"## Case: {row['case_id']}\n")
                f.write(f"**Original AI Output:**\n```json\n{row['original_ai_output']}\n```\n\n")
                f.write(f"**Corrected Diagnosis:** {row['corrected_diagnosis']}\n\n")
                f.write(f"**Human Rationale:** {row['rationale']}\n\n")
                f.write("---\n\n")
        st.success("Successfully exported to responsible_ai_log.md")
    else:
        st.warning("No corrections to export yet.")
