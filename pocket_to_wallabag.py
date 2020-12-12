#!/usr/bin/env python3
import requests
from secrets import *

# Get items from pocket
res = requests.get(
    '%s/get' % pocket_base_url,
    params={
        'consumer_key': pocket_consumer_key,
        'access_token': pocket_access_token,
    }
)
result = res.json()
urls = []
for entry_id in result["list"]:
    print(result["list"][entry_id]["given_url"])
    urls.append(result["list"][entry_id]["given_url"])

print()
print()

res = requests.get(
    "%s/oauth/v2/token" % wallabag_base_url,
    params={
        "grant_type": "password",
        "client_id": wallabag_client_id,
        "client_secret": wallabag_client_secret,
        "username": wallabag_username,
        "password": wallabag_password,
    }
)
wallabag_access_token = res.json()["access_token"]

for url in urls:
    print(url)
    res = requests.post(
        "%s/api/entries.json" % wallabag_base_url,
        headers={
            "Authorization": "Bearer %s" % wallabag_access_token
        },
        data={
            "url": url
        }
    )
    print(res)
