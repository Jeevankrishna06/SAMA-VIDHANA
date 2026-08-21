import urllib.request
import json

base = "https://sama-vidhana-1.onrender.com"

endpoints = [
    ("GET", "/health", None),
    ("GET", "/api/sources", None),
    ("POST", "/api/generate-form", {"form_type": "RTI Request", "details": {"Applicant Name": "Test", "Target Department / Opposite Party": "Dept", "Information / Remedy / Relief Demanded": "Info"}}),
    ("POST", "/api/triage", {"category": "Consumer", "description": "This is a test incident description of more than 15 chars."}),
]

for method, path, body in endpoints:
    url = base + path
    headers = {"Origin": "https://sama-vidhana.netlify.app"}
    data = None
    if body:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            print(f"[OK] {method} {path} -> {res.status}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP ERROR] {method} {path} -> HTTP {e.code}: {e.read().decode('utf-8')[:150]}")
    except Exception as e:
        print(f"[ERROR] {method} {path} -> Error: {e}")
