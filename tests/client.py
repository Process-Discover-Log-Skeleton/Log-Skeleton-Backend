"""Client test implementation for the API."""

import requests
import os

path = os.path.join(
        os.path.dirname(__file__), '../res/logs/paper-example.xes')

f = open(path, "r")
event_log = f.read()
f.close()

print('Loaded log...')

headers = {'Content-Type': 'application/xml'}

print('Calling API...')
response = requests.post(
    # 'http://localhost:5000/log-skeleton?noise-threshold=0&extended-trace=0',
    'https://log-skeleton-lzrv6ft6ka-ey.a.run.app/log-skeleton?noise-threshold=0&extended-trace=0',
    data=event_log, headers=headers)

print(response.text)
