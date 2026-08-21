import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
response = client.get("/api/sources")

print(f"STATUS_CODE: {response.status_code}")
print(f"BODY: {response.json()}")
