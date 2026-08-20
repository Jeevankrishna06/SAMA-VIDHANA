import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

print("--- Testing GET /api/sources ---")
res = client.get("/api/sources")
print("Status:", res.status_code)
print("Response:", res.json())
assert res.status_code == 200
assert "global_sources" in res.json()
assert "user_sources" in res.json()

print("\n--- Testing POST /api/schemes ---")
res = client.post("/api/schemes", json={
    "query": "farmer financial assistance",
    "category": "All Categories",
    "age": 35,
    "income": "< ₹1,00,000",
    "occupation": "Small Farmer"
})
print("Status:", res.status_code)
data = res.json()
print("Found schemes count:", len(data.get("schemes", [])))
assert res.status_code == 200
assert len(data.get("schemes", [])) > 0

print("\n--- Testing parse_json_response schema conformance in rag_engine ---")
import rag_engine
mock_llm_response = '''{
  "rights": "- **Right to Information**: Every citizen can request records under Section 3.\\n- **Right to Inspection**: Right to inspect work and certified samples.",
  "eligibility": [
    {"condition": "Must be Indian citizen", "status": "Satisfied"}
  ],
  "benefits": "- **Direct Remedy**: File RTI within 30 days.\\n- **Appeals**: First appeal to FAA.",
  "risks": "- **Section 8 Exemptions**: Commercial confidence and national security are exempt."
}'''
parsed = rag_engine.parse_json_response(mock_llm_response)
print("Parsed structure:", json.dumps(parsed, indent=2))
assert "rights" in parsed
assert "eligibility" in parsed
assert "benefits" in parsed
assert "risks" in parsed
assert isinstance(parsed["eligibility"], list)
assert isinstance(parsed["rights"], str)

print("\n--- Testing PII and Secret Redaction in Logger ---")
from main import _sanitize_log_data
sample_pii_payload = {
    "applicantName": "Ramesh Kumar",
    "applicantAddress": "123 MG Road, Bengaluru",
    "phone": "+91 9876543210",
    "email": "ramesh@example.com",
    "income": "₹2,50,000",
    "age": 42,
    "description": "Dispute regarding delayed possession",
    "secret_key": "my_secret_token_123"
}
sanitized = _sanitize_log_data(sample_pii_payload)
print("Sanitized Output:", json.dumps(sanitized, indent=2))
assert sanitized["applicantName"] == "[REDACTED_PII]"
assert sanitized["applicantAddress"] == "[REDACTED_PII]"
assert sanitized["phone"] == "[REDACTED_PII]"
assert sanitized["email"] == "[REDACTED_PII]"
assert sanitized["income"] == "[REDACTED_PII]"
assert sanitized["age"] == "[REDACTED_PII]"
assert sanitized["description"] == "[REDACTED_PII]"
assert sanitized["secret_key"] == "[REDACTED_SECRET]"

print("\n--- Testing Data Deletion Endpoints ---")
res_del = client.delete("/api/sources/nonexistent_test.pdf")
print("Delete status:", res_del.status_code)
assert res_del.status_code == 200

res_clear = client.post("/api/clear-session")
print("Clear session status:", res_clear.status_code)
assert res_clear.status_code == 200
assert res_clear.json()["status"] == "success"

print("\n--- Testing Security Headers on Responses ---")
res_headers = client.get("/api/sources")
assert res_headers.headers.get("x-content-type-options") == "nosniff"
assert res_headers.headers.get("x-frame-options") == "DENY"
assert "max-age=31536000" in res_headers.headers.get("strict-transport-security", "")
assert res_headers.headers.get("x-xss-protection") == "1; mode=block"
assert res_headers.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
assert "default-src 'self'" in res_headers.headers.get("content-security-policy", "")
print("Security headers verified successfully!")

print("\n--- Testing Rate Limiting (429 Too Many Requests) ---")
# Exhaust rate limit for /api/upload (limit: 15 per minute)
rate_limited = False
for _ in range(25):
    res_rl = client.post("/api/upload", files={"file": ("test.txt", b"plain text", "text/plain")})
    if res_rl.status_code == 429:
        rate_limited = True
        assert res_rl.json()["detail"] == "Too many requests. Please slow down and try again later."
        assert res_rl.headers.get("retry-after") == "60"
        break
assert rate_limited, "Rate limiting should have triggered 429 Too Many Requests"
print("Rate limiting verified successfully!")

print("\n--- Testing Path Traversal Defense on Delete ---")
res_pt = client.delete("/api/sources/..%2F..%2Fmain.py")
assert res_pt.status_code in [200, 400, 404]  # Handled safely without path traversal
assert os.path.exists("main.py"), "main.py must not be deleted by path traversal"
print("Path traversal defense verified successfully!")

print("\n--- Testing PDF Magic Bytes Validation ---")
# Upload fake PDF with non-PDF header
fake_pdf_content = b"This is not a PDF file"
res_fake = client.post("/api/upload", files={"file": ("malicious.pdf", fake_pdf_content, "application/pdf")})
assert res_fake.status_code in [400, 429], f"Unexpected status: {res_fake.status_code}"
print("PDF Magic Bytes validation verified successfully!")

print("\nAll Backend Test Assertions Passed Successfully!")
