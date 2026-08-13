
# NetSage AI

AI Troubleshooting Assistant for Cisco-Style Lab Networks with Mandatory Human Review.

## Features
- 30+ curated network troubleshooting cases (VLAN, gateway, DHCP, DNS, routing, ACL, NAT, wireless)
- Deterministic rule checker for mechanical config errors
- AI diagnosis using Groq (Llama 3.3 70B) with strict JSON schema validation
- Mandatory human review workflow (Accept / Edit / Reject)
- Metrics dashboard with AI vs. human agreement tracking
- Responsible AI log for corrected diagnoses

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key:
```bash
export GROQ_API_KEY="gsk_..."
```

Initialize the database and run the pipeline:
```bash
python orchestrator.py
```

Run the app:
```bash
streamlit run app.py
```
>>>>>>> cb70efe (Initial commit: NetSage AI Troubleshooting Assistant)
