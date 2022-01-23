# An example client to interact with ddash

import base64
import json
import os
import re
import requests
import logging

from glob import glob
from copy import deepcopy

logger = logging.getLogger(__name__)


class DDashClient:
    def __init__(self, host=None, port=None, token=None, username=None):
        self.host = host or "http://127.0.0.1"
        self.port = port or "8000"
        self.prefix = "api"
        self.token = os.environ.get("DDASH_TOKEN", token)
        self.username = os.environ.get("DDASH_USER", username)
        self.session = requests.Session()
        self.headers = {}

    def set_header(self, name, value):
        self.headers.update({name: value})

    @property
    def baseurl(self):
        if self.port:
            return self.host.strip('/') + ":" + self.port + "/" + self.prefix
        return self.host.strip('/') + "/" + self.prefix

    def set_basic_auth(self, username, password):
        """
        A wrapper to adding basic authentication to the Request
        """
        auth_header = get_basic_auth(username, password)
        if isinstance(auth_header, bytes):
            auth_header = auth_header.decode("utf-8")
        self.set_header("Authorization", "Basic %s" % auth_header)

    def reset(self):
        """
        Reset and prepare for a new request.
        """
        if "Authorization" in self.headers:
            self.headers = {"Authorization": self.headers["Authorization"]}
        else:
            self.headers = {}

    def do_request(self, endpoint, method="GET", data=None, headers=None, files=None):
        """
        Do a request. This is a wrapper around requests.
        """

        # Always reset headers for new request.
        self.reset()

        headers = headers or {}
        url = "%s/%s" % (self.baseurl, endpoint)

        # Make the request and return to calling function, unless requires auth
        response = self.session.request(method, url, data=data, headers=headers, files=files)

        # A 401 response is a request for authentication
        if response.status_code != 401:
            return response

        # Otherwise, authenticate the request and retry
        if self.authenticate_request(response):
            return self.session.request(method, url, data=data, headers=self.headers)
        return response

    def authenticate_request(self, originalResponse):
        """
        Authenticate Request

        Given a response, look for a Www-Authenticate header to parse. We
        return True/False to indicate if the request should be retried.
        """
        authHeaderRaw = originalResponse.headers.get("Www-Authenticate")
        if not authHeaderRaw:

            return False

        # If we have a username and password, set basic auth automatically
        if self.token and self.username:
            self.set_basic_auth(self.username, self.token)

        headers = deepcopy(self.headers)
        if "Authorization" not in headers:
            logger.error(
                "This endpoint requires a token. Please set "
                "client.set_basic_auth(username, password) first "
                "or export them to the environment."
            )
            return False

        # Prepare request to retry
        h = parse_auth_header(authHeaderRaw)
        headers.update(
            {
                "service": h.Service,
                "Accept": "application/json",
                "User-Agent": "ddash-cli",
            }
        )

        # Currently we don't set a scope (it defaults to build)
        authResponse = self.session.request("GET", h.Realm, headers=headers)
        if authResponse.status_code != 200:
            return False

        # Request the token
        info = authResponse.json()
        token = info.get("token")
        if not token:
            token = info.get("access_token")

        # Set the token to the original request and retry
        self.headers.update({"Authorization": "Bearer %s" % token})
        return True

    # Functions correspond to endpoints
    def service_info(self):
        """get the service information endpoint"""
        # Base endpoint provides service info
        response = self.do_request("")
        return response.json()

    def upload_result(self, result_json, test_log=None, dyninst_build_log=None, test_build_log=None):
        """Upload a result, which includes a json file and optionally three logs:
       
         - test_log is associated with the main test result
         - dyninst_build_log is for the dyninst BuildResult
         - testsuite_build_log is for the testsuite BuildResult
        """
        response = self.upload_result_json(result_json)
        print(response.get('message'))
        if response.get('code') == 201:
            run_id = 10 #response.get('data', {}).get('test_run')
            if run_id and test_log:
                self.upload_result_log(test_log, run_id, "test_log")
            if run_id and dyninst_build_log:
                self.upload_result_log(dyninst_build_log, run_id, "dyninst_build_log")
            if run_id and test_build_log:
                self.upload_result_log(test_build_log, run_id, "test_build_log")

    def upload_result_json(self, result_json):
        """
        Upload just a json test result.
        """
        result = read_json(result_json)
        return self.do_request("results/new/", "POST", data=json.dumps({"result": result}))

    def upload_result_log(self, filename, run_id, log_type):
        """
        Upload some kind of result log.
        """
        data = {"run_id": run_id, "log_type": log_type}
        files = {'logfile': open(filename, 'rb')}
        return self.do_request("results/log/", "POST", data=data, files=files)


# Helper functions


def get_basic_auth(username, password):
    auth_str = "%s:%s" % (username, password)
    return base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")


def parse_auth_header(authHeaderRaw):
    """
    Parse authentication header into pieces
    """
    regex = re.compile('([a-zA-z]+)="(.+?)"')
    matches = regex.findall(authHeaderRaw)
    lookup = dict()
    for match in matches:
        lookup[match[0]] = match[1]
    return authHeader(lookup)


class authHeader:
    def __init__(self, lookup):
        """
        Given a dictionary of values, match them to class attributes
        """
        for key in lookup:
            if key in ["realm", "service", "scope"]:
                setattr(self, key.capitalize(), lookup[key])


def read_file(filename):
    with open(filename, "r") as fd:
        content = fd.read()
    return content


def read_json(filename):
    return json.loads(read_file(filename))
