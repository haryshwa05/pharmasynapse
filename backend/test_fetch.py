# backend/test_ct_fetch.py
import requests, sys

url = "https://clinicaltrials.gov/api/v2/studies?query.term=montelukast&pageSize=20"
h = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Referer": "https://clinicaltrials.gov/",
    "Accept-Language": "en-US,en;q=0.9"
}

try:
    r = requests.get(url, headers=h, timeout=20)
    print("status:", r.status_code)
    if r.ok:
        j = r.json()
        studies = j.get("studies", [])
        if studies:
            first = studies[0]
            title = first.get("protocolSection", {}).get("identificationModule", {}).get("briefTitle")
            print("first title:", title)
        else:
            print("no studies returned")
    else:
        print("body (first 400 chars):", r.text[:400])
except Exception as e:
    print("request failed:", repr(e))
    sys.exit(1)
