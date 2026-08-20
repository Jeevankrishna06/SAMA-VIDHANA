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

print("\nAll Backend Test Assertions Passed Successfully!")
