import sqlite3
import json
import csv

DB_FILE = 'netsage.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            symptom TEXT,
            topology_note TEXT,
            show_output TEXT,
            expected_fault TEXT,
            osi_layer TEXT,
            concept_tag TEXT,
            severity TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS diagnoses (
            diagnosis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            raw_ai_response TEXT,
            root_cause TEXT,
            confidence TEXT,
            evidence TEXT,
            next_command TEXT,
            fix_steps TEXT,
            rule_findings TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(case_id) REFERENCES cases(case_id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            diagnosis_id INTEGER,
            decision TEXT,
            corrected_root_cause TEXT,
            rationale TEXT,
            reviewer TEXT,
            reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(case_id) REFERENCES cases(case_id),
            FOREIGN KEY(diagnosis_id) REFERENCES diagnoses(diagnosis_id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS responsible_ai_log (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            original_ai_output TEXT,
            corrected_diagnosis TEXT,
            rationale TEXT,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def load_cases_from_csv(csv_path='cases.csv'):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            c.execute('''
                INSERT OR IGNORE INTO cases (case_id, symptom, topology_note, show_output, expected_fault, osi_layer, concept_tag, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (row['case_id'], row['symptom'], row['topology_note'], row['show_output'], row['expected_fault'], row['osi_layer'], row['concept_tag'], row['severity']))
    conn.commit()
    conn.close()

def save_diagnosis(case_id, diagnosis_obj, rule_findings):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    fix_steps_str = json.dumps(diagnosis_obj.fix_steps) if diagnosis_obj else "[]"
    rule_findings_str = json.dumps(rule_findings)
    raw_ai = diagnosis_obj.model_dump_json() if diagnosis_obj else "{}"

    c.execute('''
        INSERT INTO diagnoses (case_id, raw_ai_response, root_cause, confidence, evidence, next_command, fix_steps, rule_findings)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        case_id,
        raw_ai,
        diagnosis_obj.root_cause if diagnosis_obj else "",
        diagnosis_obj.confidence if diagnosis_obj else "",
        diagnosis_obj.evidence if diagnosis_obj else "",
        diagnosis_obj.next_command if diagnosis_obj else "",
        fix_steps_str,
        rule_findings_str
    ))
    
    diagnosis_id = c.lastrowid
    conn.commit()
    conn.close()
    return diagnosis_id

def save_review(case_id, diagnosis_id, decision, corrected_root_cause, rationale, reviewer="Student"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO reviews (case_id, diagnosis_id, decision, corrected_root_cause, rationale, reviewer)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (case_id, diagnosis_id, decision, corrected_root_cause, rationale, reviewer))
    
    if decision in ['Edited', 'Rejected']:
        c.execute('SELECT raw_ai_response FROM diagnoses WHERE diagnosis_id = ?', (diagnosis_id,))
        row = c.fetchone()
        raw_ai = row[0] if row else ""
        c.execute('''
            INSERT INTO responsible_ai_log (case_id, original_ai_output, corrected_diagnosis, rationale)
            VALUES (?, ?, ?, ?)
        ''', (case_id, raw_ai, corrected_root_cause, rationale))

    conn.commit()
    conn.close()

def get_all_cases():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM cases')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == '__main__':
    init_db()
    load_cases_from_csv()
    print("Database initialized and cases loaded.")
