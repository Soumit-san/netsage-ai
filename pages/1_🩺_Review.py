import streamlit as st
import sqlite3
import pandas as pd
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import db

def get_unreviewed_diagnoses():
    conn = sqlite3.connect(db.DB_FILE)
    query = '''
        SELECT d.diagnosis_id, c.case_id, c.symptom, c.topology_note, c.show_output, c.expected_fault,
               d.root_cause, d.confidence, d.evidence, d.next_command, d.fix_steps, d.rule_findings
        FROM diagnoses d
        JOIN cases c ON d.case_id = c.case_id
        LEFT JOIN reviews r ON d.diagnosis_id = r.diagnosis_id
        WHERE r.review_id IS NULL
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.title("🩺 Human Review Workflow")

df_unreviewed = get_unreviewed_diagnoses()

if df_unreviewed.empty:
    st.success("✅ All AI diagnoses have been reviewed!")
else:
    st.markdown(f"**{len(df_unreviewed)}** cases pending review.")
    
    case_idx = st.selectbox("Select Case", range(len(df_unreviewed)), format_func=lambda x: df_unreviewed.iloc[x]['case_id'])
    selected = df_unreviewed.iloc[case_idx]
    
    st.header(f"Case: {selected['case_id']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Case Evidence")
        st.markdown(f"**Symptom:** {selected['symptom']}")
        st.markdown(f"**Topology Note:** {selected['topology_note']}")
        st.text_area("Show Output", selected['show_output'], height=200, disabled=True)
        st.info(f"**Ground Truth (Expected Fault):** {selected['expected_fault']}")
        
        st.subheader("🔧 Deterministic Rule Findings")
        try:
            findings = json.loads(selected['rule_findings'])
            if findings:
                st.json(findings)
            else:
                st.write("No deterministic rule violations found.")
        except:
            st.write("No findings data available.")
            
    with col2:
        st.subheader("🤖 AI Diagnosis")
        st.markdown(f"**Root Cause:** {selected['root_cause']}")
        st.markdown(f"**Confidence:** {selected['confidence']}")
        st.markdown(f"**Evidence:** {selected['evidence']}")
        st.markdown(f"**Next Command:** `{selected['next_command']}`")
        
        try:
            fixes = json.loads(selected['fix_steps'])
            if fixes:
                st.markdown("**Fix Steps:**")
                for f in fixes:
                    st.markdown(f"- `{f}`")
        except:
            pass
            
        st.divider()
        st.subheader("✍️ Review Decision")
        
        with st.form("review_form"):
            decision = st.radio("Decision", ["Accepted", "Edited", "Rejected"])
            corrected_root_cause = st.text_input("Corrected Root Cause (Required if Edited/Rejected)", "")
            rationale = st.text_area("Rationale (Required if Edited/Rejected)", "")
            
            submitted = st.form_submit_button("Submit Review")
            
            if submitted:
                if decision in ["Edited", "Rejected"] and (not corrected_root_cause or not rationale):
                    st.error("Please provide the corrected root cause and rationale for Edited/Rejected decisions.")
                else:
                    db.save_review(
                        selected['case_id'], 
                        int(selected['diagnosis_id']), 
                        decision, 
                        corrected_root_cause, 
                        rationale
                    )
                    st.success("✅ Review submitted successfully!")
                    st.rerun()
