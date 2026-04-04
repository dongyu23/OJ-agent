import requests

try:
    response = requests.get('http://127.0.0.1:8000/')
    print("Status Code:", response.status_code)
    print("Content:", response.text[:200])
except Exception as e:
    print("Error:", e)
