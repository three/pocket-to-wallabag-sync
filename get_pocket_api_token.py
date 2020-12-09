#!/usr/bin/env python3
import sys
import requests

HELP_TEXT = """Usage: get_pocket_api_token <consumer_key>
"""

REDIRECT_URI = "data:,return%sto%scli"

if len(sys.argv) != 2:
    sys.stderr.write(HELP_TEXT)
    exit(1)

if sys.argv[1] == "--help":
    sys.stdout.write(HELP_TEXT)
    exit(0)

def pocket_post(path, data):
    r = requests.post(
        "https://getpocket.com/v3%s" % path,
        json=data,
        headers={
            "Content-Type":"application/json",
            "X-Accept":"application/json"
        }
    )
    if r.status_code != 200:
        print("The Pocket API returned an error, aborting")
        print("X-Error-Code: %s" % r.headers.get("X-Error-Code"))
        print("X-Error: %s" % r.headers.get("X-Error"))
        exit(2)

    return r.json()

code = pocket_post(
    "/oauth/request",
    {
        "consumer_key": sys.argv[1],
        "redirect_uri": REDIRECT_URI
    }
)["code"]

print("Please go to the URL below to authorize Pocket")
print()
print("https://getpocket.com/auth/authorize?request_token=%s&redirect_uri=about:blank" % code)
print()
input("Press Enter after authorization")
print()

print(pocket_post(
    "/oauth/authorize",
    {
        "consumer_key": sys.argv[1],
        "code": code
    }
))
