# This examples shows how to get (and print) service info for a running ddash server

import os
import sys
import json

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(here))

from ddashcli import DDashClient

# defaults to host=http:127.0.0.1 and host 8000
client = DDashClient()
info = client.service_info()

# Make it pretty to print to the screen
print(json.dumps(info, indent=4))

"""
{'id': 'ddash',
 'status': 'running',
 'name': 'Dyninst Dashboard (ddash)',
 'description': 'This service provides a dashboard for Dyninst results',
 'organization': {'name': 'dyninst', 'url': 'https://github.com/dyninst'},
 'contactUrl': 'https://github.com/dyninst/dashboard/issues',
 'documentationUrl': 'https://github.com/dyninst/dashboard',
 'createdAt': '2022-01-14T17:47:16Z',
 'updatedAt': '2022-01-15T19:09:09Z',
 'environment': 'test',
 'version': '0.0.1',
 'auth_instructions_url': 'OAauth2 is currently disabled.'}
"""
