import urllib.request
import json

url = "https://sama-vidhana-1.onrender.com/api/chat"

# Test 1: OPTIONS preflight
print("--- TEST 1: OPTIONS Preflight ---")
req_opt = urllib.request.Request(
    url,
    headers={
        "Origin": "https://sama-vidhana.netlify.app",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    },
    method="OPTIONS"
)
try:
    with urllib.request.urlopen(req_opt) as res:
        print("OPTIONS Status:", res.status)
        print("OPTIONS Headers:")
        for k, v in res.headers.items():
            if "access-control" in k.lower():
                print(f"  {k}: {v}")
except urllib.error.HTTPError as e:
    print(f"OPTIONS Error {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"OPTIONS Exception: {e}")

# Test 2: POST /api/chat
print("\n--- TEST 2: POST /api/chat ---")
data = json.dumps({"question": "What is RTI?"}).encode("utf-8")
req_post = urllib.request.Request(
    url,
    data=data,
    headers={
        "Origin": "https://sama-vidhana.netlify.app",
        "Content-Type": "application/json",
    },
    method="POST"
)
try:
    with urllib.request.urlopen(req_post) as res:
        print("POST Status:", res.status)
        print("POST Headers:")
        for k, v in res.headers.items():
            if "access-control" in k.lower():
                print(f"  {k}: {v}")
        print("POST Body:", res.read().decode("utf-8")[:200])
except urllib.error.HTTPError as e:
    print(f"POST Error {e.code}: {e.read().decode('utf-8')}")
    print("POST Error Headers:")
    for k, v in e.headers.items():
        if "access-control" in k.lower():
            print(f"  {k}: {v}")
except Exception as e:
    print(f"POST Exception: {e}")
