import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import rag_engine

# Test Case 1: Markdown output with ### headers
md_text = """### Rights
- **Right to Information**: Citizens have the right to request public records.
- **Right to Inspection**: Citizens can inspect work and documents.

### Eligibility
- Must be an Indian citizen (Satisfied)
- Must pay application fee of Rs 10 (Required)

### Benefits
- Access government data within 30 days.
- Escalate to First Appellate Authority if rejected.

### Risks
- Section 8 exemptions apply to national security.
"""

r1 = rag_engine.parse_json_response(md_text)
print("--- TEST 1 (Markdown) ---")
print(r1)
assert isinstance(r1["rights"], str)
assert isinstance(r1["eligibility"], list)
assert isinstance(r1["benefits"], str)
assert isinstance(r1["risks"], str)
assert len(r1["eligibility"]) == 2
assert r1["eligibility"][0]["condition"] == "Must be an Indian citizen"
assert r1["eligibility"][0]["status"] == "Satisfied"

# Test Case 2: Capitalized JSON array output
json_text = """{
  "Rights": ["Right to information", "Right to inspection"],
  "Eligibility": [{"Condition": "Must be citizen", "Status": "Satisfied"}],
  "Benefits": ["Access government data within 30 days"],
  "Risks": ["Exemptions apply"]
}"""

r2 = rag_engine.parse_json_response(json_text)
print("\n--- TEST 2 (Capitalized JSON Arrays) ---")
print(r2)
assert isinstance(r2["rights"], str)
assert "- Right to information" in r2["rights"]
assert isinstance(r2["eligibility"], list)
assert r2["eligibility"][0]["condition"] == "Must be citizen"
assert r2["eligibility"][0]["status"] == "Satisfied"
assert isinstance(r2["benefits"], str)
assert isinstance(r2["risks"], str)

# Test Case 3: Mixed case JSON with string values
json_text_3 = """{
  "RIGHTS": "- Right 1\\n- Right 2",
  "ELIGIBILITY": [{"condition": "Fee paid", "status": "Required"}],
  "BENEFITS": "- Benefit 1",
  "RISKS": "- Risk 1"
}"""
r3 = rag_engine.parse_json_response(json_text_3)
print("\n--- TEST 3 (Upper Case Keys) ---")
print(r3)
assert isinstance(r3["rights"], str)
assert isinstance(r3["eligibility"], list)
assert r3["eligibility"][0]["condition"] == "Fee paid"

print("\nALL 3 TESTS PASSED PERFECTLY!")
