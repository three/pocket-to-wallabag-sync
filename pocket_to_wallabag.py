#!/usr/bin/env python3
import requests
import argparse
import re

POCKET_HEADERS = {
    'Content-Type': 'application/json',
    'X-Accept': 'application/json'
}

settings_file = None
settings = []

def init_settings(fname):
    global settings_file
    global settings
    print(settings)
    settings_file = open(fname, 'a+', encoding='utf-8')
    settings_file.seek(0)
    for line in settings_file:
        match = re.match(r'^([a-z_]+) +([a-zA-Z0-9_-]+)\n$', line)
        if match:
            settings.append(match.groups())
        else:
            settings.append((line,))
    print(settings)

def get_setting(setting_name):
    global settings
    for setting in settings:
        if len(setting) == 2 and setting[0] == setting_name:
            return setting[1]
    return None

def set_setting(name, value):
    global settings_file
    global settings

    if not re.search(r'^[a-z_]+$', name):
        print('Invalid Setting Name. Aborting.')
        exit(1)

    if not re.search(r'^[A-Za-z0-9_-]+$', value):
        print('Invalid Setting Value. Aborting.')
        exit(1)

    index = None
    for i in range(len(settings)):
        if len(settings[i]) == 2 and settings[i][0] == name:
            index = i
            break
    if index:
        settings[index] = (name, value)
    else:
        settings.append((name, value))

    settings_file.truncate(0)
    for setting in settings:
        if len(setting) == 1:
            settings_file.write(setting[0])
        else:
            settings_file.write(' '.join(setting) + '\n')

def pocket_check_response_valid(res):
    if res.status_code != 200:
        print('The Pocket API returned an error')
        print("X-Error-Code: %s" % res.headers.get("X-Error-Code"))
        print("X-Error: %s" % res.headers.get("X-Error"))
        return False
    else:
        return True

def setup_pocket():
    consumer_key = get_setting('pocket_consumer_key')
    print('Your Pocket Consumer Key: %s' % consumer_key)
    if not consumer_key:
        consumer_key = input('Please Enter a Valid Consumer Key: ')
        set_setting('pocket_consumer_key', consumer_key)
    print()

    if get_setting('pocket_access_token'):
        print('This will override your current Pocket access token')
        input('Press Enter to Continue')
        print()

    print('Attempting to get an access token...')
    res_req = requests.post(
        'https://getpocket.com/v3/oauth/request',
        headers=POCKET_HEADERS,
        json={
            'consumer_key': consumer_key,
            'redirect_uri': 'about:blank'
        }
    )
    if not pocket_check_response_valid(res_req):
        print('Aborting')
        exit(1)

    code = res_req.json()['code']
    print('\nPlease go to the URL below to authorize Pocket\n')
    print('    https://getpocket.com/auth/authorize?request_token=%s&redirect_uri=about:blank\n' % code)
    input('Press Enter after authorization')

    res_auth = requests.post(
        'https://getpocket.com/v3/oauth/authorize',
        headers=POCKET_HEADERS,
        json={
            'consumer_key': consumer_key,
            'code': code
        }
    )
    if not pocket_check_response_valid(res_auth):
        print('Aborting')
        exit(1)
    
    access_token = res_auth.json()['access_token']
    print('\nSuccessfully recieved Pocket Access Token: %s' % access_token)
    set_setting('pocket_access_token', access_token)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', default='./pocket2wallabag_db.txt')
    parser.add_argument('command')
    args = parser.parse_args()

    init_settings(args.f)

    if args.command == 'setup_pocket':
        setup_pocket()

if __name__ == '__main__':
    main()
