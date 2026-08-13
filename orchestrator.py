from rule_checker import RuleChecker
from diagnose import diagnose_case
import db

def process_case(case):
    print(f"Processing case: {case['case_id']}")
    
    # 1. Run deterministic rule checker
    checker = RuleChecker()
    findings = checker.check_all(case)
    print(f"  - Found {len(findings)} deterministic findings.")
    
    # 2. Run AI Diagnosis
    diagnosis = diagnose_case(case, findings)
    if diagnosis:
        print(f"  - AI Diagnosis successful: {diagnosis.root_cause[:50]}...")
    else:
        print("  - AI Diagnosis failed.")
        
    # 3. Save to database
    diagnosis_id = db.save_diagnosis(case['case_id'], diagnosis, findings)
    print(f"  - Saved as Diagnosis ID {diagnosis_id}")
    
    return diagnosis_id

if __name__ == '__main__':
    # Initialize DB and load cases if not already done
    db.init_db()
    db.load_cases_from_csv()
    
    # Process all cases
    cases = db.get_all_cases()
    for case in cases:
        process_case(case)
