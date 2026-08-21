import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# 1. Test CORS preflight (OPTIONS request) from Netlify origin
print("Testing CORS OPTIONS preflight from https://sama-vidhana.netlify.app...")
headers = {
    "Origin": "https://sama-vidhana.netlify.app",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type",
}
res_opt = client.options("/api/chat", headers=headers)
print("OPTIONS status code:", res_opt.status_code)
print("Access-Control-Allow-Origin:", res_opt.headers.get("access-control-allow-origin"))
print("Access-Control-Allow-Credentials:", res_opt.headers.get("access-control-allow-credentials"))
print("Access-Control-Allow-Methods:", res_opt.headers.get("access-control-allow-methods"))

assert res_opt.status_code == 200
assert res_opt.headers.get("access-control-allow-origin") == "https://sama-vidhana.netlify.app"

# 2. Test GET /health with Netlify origin
res_health = client.get("/health", headers={"Origin": "https://sama-vidhana.netlify.app"})
print("\nGET /health status:", res_health.status_code)
print("Access-Control-Allow-Origin:", res_health.headers.get("access-control-allow-origin"))
assert res_health.headers.get("access-control-allow-origin") == "https://sama-vidhana.netlify.app"

print("\nCORS preflight & requests from Netlify origin verified successfully!")
