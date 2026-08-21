import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
import main
from main import app

client = TestClient(app)

# 1. Test /health (Should be instant and not initialize GLOBAL_VS or embeddings)
print("Testing GET /health...")
res_health = client.get("/health")
print(f"GET /health -> Status: {res_health.status_code}, Body: {res_health.json()}")
assert res_health.status_code == 200
assert res_health.json() == {"status": "ok"}
print(f"GLOBAL_VS initialized after /health? {main.GLOBAL_VS is not None}")
assert main.GLOBAL_VS is None, "GLOBAL_VS should NOT be initialized by /health"

# 2. Test /api/sources (Should return list of sources without initializing GLOBAL_VS or embeddings)
print("\nTesting GET /api/sources...")
res_sources = client.get("/api/sources")
print(f"GET /api/sources -> Status: {res_sources.status_code}")
print(f"Global sources count: {len(res_sources.json().get('global_sources', []))}")
assert res_sources.status_code == 200
print(f"GLOBAL_VS initialized after /api/sources? {main.GLOBAL_VS is not None}")
assert main.GLOBAL_VS is None, "GLOBAL_VS should NOT be initialized by /api/sources"

print("\nAll tests passed successfully! Startup and monitoring endpoints are 100% lightweight and decoupled from ML models.")
