import json

import ddash.settings as settings
import logging

logger = logging.getLogger(__name__)

# Valid build statuses

TEST_RUN_STATUS = [
    ("OK", "OK"),
    ("FAILED", "FAILED"),
    ("FAILOVER", "FAILOVER"),
    ("NOTRUN", "NOTRUN"),
]

TEST_BUILD_STATUS = [
    ("NOTBUILT", "NOTBUILT"),
    ("OK", "OK"),
    ("FAILED", "FAILED"),
]

TEST_RESULT_STATUS = [
    ("FAILED", "FAILED"),
    ("CRASHED", "CRASHED"),
    ("SKIPPED", "SKIPPED"),
    ("PASSED", "PASSED"),
    ("HANGED", "HANGED"),
]

TEST_MODES = [
    # rewrite: take an executable, modify, write a new one to disk, execute it
    ("rewriter", "rewriter"),
    # attach: attach to a running process
    ("attach", "attach"),
    ("create", "create"),
    ("disk", "disk"),
]

LANGUAGES = [
    ("C", "C"),
    ("C++", "C++"),
    ("Fortran", "Fortran"),
]


def get_upload_folder(instance, filename):
    root = os.path.join(settings.MEDIA_ROOT, instance.id)
    upload_dir = os.path.join(root, "logs")
    for dirname in [root, upload_dir]:
        if not os.path.exists(dirname):
            os.mkdir(dirname)
    return os.path.join(upload_dir, filename)


def read_json(filename):
    with open(filename, "r") as fd:
        content = json.loads(fd.read())
    return content
