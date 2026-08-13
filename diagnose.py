import os
import json
from pydantic import BaseModel, ValidationError
from typing import List
from groq import Groq

# Pydantic Schema for AI Diagnosis
class DiagnosisResult(BaseModel):
    root_cause: str
    confidence: str
    evidence: str
    next_command: str
    fix_steps: List[str]

def load_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), 'diagnose_prompt.md')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

def diagnose_case(case_data, rule_findings, api_key=None):
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        # Fallback to a mock response for testing without API keys
        return DiagnosisResult(
            root_cause="Mocked root cause (API Key missing)",
            confidence="High",
            evidence="Mocked evidence from show output",
            next_command="show mock",
            fix_steps=["Mock step 1", "Mock step 2"]
        )

    client = Groq(api_key=api_key)
    
    prompt_template = load_prompt()
    
    # Format the prompt using replace to avoid conflicts with JSON curly braces
    formatted_prompt = prompt_template.replace('{symptom}', case_data.get('symptom', ''))
    formatted_prompt = formatted_prompt.replace('{topology_note}', case_data.get('topology_note', ''))
    formatted_prompt = formatted_prompt.replace('{show_output}', case_data.get('show_output', ''))
    formatted_prompt = formatted_prompt.replace('{rule_findings}', json.dumps(rule_findings, indent=2))

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a Cisco network troubleshooting assistant. Always return valid JSON matching the schema."},
                {"role": "user", "content": formatted_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        response_content = response.choices[0].message.content
        
        # Parse and validate with Pydantic
        parsed_json = json.loads(response_content)
        diagnosis = DiagnosisResult(**parsed_json)
        return diagnosis
        
    except ValidationError as e:
        print(f"Validation Error: {e}")
        return None
    except Exception as e:
        print(f"API Error: {e}")
        return None

if __name__ == '__main__':
    # Test execution
    test_case = {
        'symptom': 'PC cannot ping its default gateway.',
        'topology_note': 'PC is on switchport Fa0/1, should be in VLAN 10.',
        'show_output': 'Switch# show vlan brief\n1    default                          active    Fa0/1'
    }
    result = diagnose_case(test_case, [])
    print(result.model_dump_json(indent=2))
