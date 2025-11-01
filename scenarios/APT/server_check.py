import requests

def check_get(url: str):
    try:
        r = requests.get(url, timeout=5)
        print(f"GET {url} -> {r.status_code} {r.reason}")
        print("Response body (first 300 chars):", r.text[:300])
    except Exception as e:
        print("GET failed:", e)

def check_upload(url: str):
    # harmless test file content (no system info)
    files = {"file": ("test.txt", b"hello-server-check\n")}
    try:
        r = requests.post(url, files=files, timeout=10)
        print(f"POST {url} -> {r.status_code} {r.reason}")
        print("Response (first 300 chars):", r.text[:300])
    except Exception as e:
        print("POST failed:", e)


base="http://20.93.23.234:8000"
#base="http://127.0.0.1:8081"
check_get(base+"/")
check_upload(base + "/upload")