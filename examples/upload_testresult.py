#!/usr/bin/env python

# upload_testresult is an example of using the restful API to upload a test result
# A test result includes:
# - a json dump of metadata and results listing
# - (optionally but likely) a log file
#
# Since this is an API endpoint, you are required to have authentication.
# meaning you should export your username and token
#
# export DDASH_TOKEN=xxxxxxxxxxxxxxxxxx
# export DDASH_USER=thebestdude

# Usage
# python upload_testresult.py data/example_results.json data/d339ca31dbcb698174e560bc85e222cae8dc3321b848911de7315924fc4a6bc9.tar.gz

import os
import json
import sys

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(here))

from ddashcli import DDashClient

# If the user doesn't provide a spec file, ask for it
if len(sys.argv) < 3:
    sys.exit(
        "Please provide the results json file and log file to upload."
    )

# Upload json file and log file
upload_file = os.path.abspath(sys.argv[1])

# We are assuming this is the test log, dyninst and testresult build log. 
# In reality these would be different files, and they aren't required.
log_file = sys.argv[2]

for filename in [upload_file, log_file]:
    if not os.path.exists(filename):
        sys.exit("%s does not exist." % filename)

# The spackmoncli doesn't enforce this since auth can be disabled, so we do here
#token = os.environ.get("DDASH_TOKEN")
#username = os.environ.get("DDASH_USER")

#if not username or not token:
#    sys.exit("You are required to export your DDASH_TOKEN and DDASH_USER")

# defaults to host=http:127.0.0.1 and prefix=ms1
client = DDashClient()

# We are cheating here and providing the same file for all three logs!
response = client.upload_result(upload_file, test_log=log_file, dyninst_build_log=log_file, test_build_log=log_file)
print(response)
