from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import authenticate
from ddash.apps.main.models import *
from datetime import datetime
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
import sqlite3
import sys
import os
import re

tables_query = (
    "SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';"
)
fields_query = "PRAGMA table_info(%s);"
test_result_query = "SELECT * FROM test_result WHERE runid=%s;"
select_all_query = "SELECT * FROM %s;"


class Conn:
    def __init__(self, db_file):
        self.conn = None
        self.db_file = db_file
        self.connect()

    def __exit__(self):
        self.conn.close()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
        except Exception as e:
            sys.exit(e)

    def run_query(self, query):
        cur = self.conn.cursor()
        cur.execute(query)
        return cur.fetchall()


def add_test_modes(conn):
    print("Adding TestMode")
    modes = [x[0] for x in conn.run_query(select_all_query % "mode")]
    for mode in modes:
        TestMode.objects.get_or_create(name=mode)


def add_compilers(conn):
    print("Adding Compiler")
    compiler_id_lookup = {}
    compilers = conn.run_query(select_all_query % "compiler")
    fields = [x[1] for x in conn.run_query(fields_query % "compiler")]

    idx = {}
    for field in fields:
        idx[field] = fields.index(field)

    for c in compilers:
        new_compiler, _ = Compiler.objects.get_or_create(
            name=c[idx["name"]],
            version=c[idx["version"]],
            language=c[idx["language"]],
            path=c[idx["path"]],
        )
        compiler_id_lookup[c[idx["id"]]] = new_compiler.id

    return compiler_id_lookup


class Command(BaseCommand):
    """Import Tim's previous version of the database to the models here."""

    def add_arguments(self, parser):
        parser.add_argument("db", nargs=1, default=None, type=str)

    help = "Import the previous version of the sqlite database"

    def handle(self, *args, **options):
        if not options["db"]:
            raise CommandError("Please provide a sqlite3 database to import.")
        db = options["db"][0]
        if not os.path.exists(db):
            sys.exit("%s does not exist!" % db)
        print("sqlite3 database is: %s" % db)

        # Connect to the file
        conn = Conn(db)
        tables = [x[0] for x in conn.run_query(tables_query)]

        # Confirm we aren't missing anything
        known_tables = [
            "link_type",
            "status",
            "mode",
            "test_result",
            "run",
            "run_compiler",
            "compiler",
            "auth_token",
            "regression_count",
        ]
        for known_table in known_tables:
            if known_table not in tables:
                sys.exit("%s is not a recognized table to this script." % known_table)

        # Read in tables strategically
        add_test_modes(conn)

        # We keep compiler under the same model
        # Keep a lookup of old ids to new ones
        compiler_id_lookup = add_compilers(conn)
        test_run_lookup, test_result_lookup = add_runs(conn)

        # Finally, add regressions
        add_regressions(conn, test_run_lookup)


def add_regressions(conn, test_run_lookup):
    print("Adding Regressions")
    regs = conn.run_query(select_all_query % "regression_count")
    fields = [x[1] for x in conn.run_query(fields_query % "regression_count")]
    idx = {}
    for field in fields:
        idx[field] = fields.index(field)

    for reg in regs:
        try:
            previous_run = TestRun.objects.get(id=test_run_lookup[reg[idx["prev_run"]]])
        except:
            previous_run = None

        try:
            next_run = TestRun.objects.get(id=test_run_lookup[reg[idx["next_run"]]])
        except:
            next_run = None
        regression, _ = Regressions.objects.get_or_create(
            previous_run=previous_run, next_run=next_run, count=reg[idx["count"]]
        )


def add_runs(conn):
    print("Adding TestRun")
    runs = conn.run_query(select_all_query % "run")
    fields = [x[1] for x in conn.run_query(fields_query % "run")]

    idx = {}
    for field in fields:
        idx[field] = fields.index(field)

    # We will need test result fields too
    result_fields = [x[1] for x in conn.run_query(fields_query % "test_result")]
    ridx = {}
    for field in result_fields:
        ridx[field] = result_fields.index(field)

    # Keep track of test run lookup to add results to
    test_run_lookup = {}
    test_result_lookup = {}

    for run in runs:

        # Derive the PR id either from dyninst or testsuite (I checked, it's either OR)
        if "PR" in run[idx["dyninst_branch"]]:
            pr_id = re.sub("(PR|pr)", "", run[idx["dyninst_branch"]])
            pr, _ = PullRequest.objects.get_or_create(
                url="https://github.com/dyninst/dyninst/pull/%s" % pr_id,
                user="unknown",
                pr_id=int(pr_id),
            )
        elif "PR" in run[idx["testsuite_branch"]]:
            pr_id = re.sub("(PR|pr)", "", run[idx["testsuite_branch"]])
            pr, _ = PullRequest.objects.get_or_create(
                url="https://github.com/dyninst/testsuite/pull/%s" % pr_id,
                user="unknown",
                pr_id=int(pr_id),
            )

        # No PR if, we use unknown!
        else:
            pr = None

        # Create libc dependnecy first
        dep, _ = Dependency.objects.get_or_create(name="libc", version=run[idx["libc"]])

        # Do a query to see if we have the environment first
        # NOTE: this assumes we don't have environments with NO dependencies
        envs = Environment.objects.filter(
            hostname=run[idx["hostname"]],
            arch=run[idx["arch"]],
            kernel=run[idx["kernel"]],
            host_os=run[idx["os"]],
            dependencies__in=[dep],
        )
        if not envs:

            # Assert that we don't have the same environment with no dependencies
            envs = Environment.objects.filter(
                hostname=run[idx["hostname"]],
                arch=run[idx["arch"]],
                kernel=run[idx["kernel"]],
                host_os=run[idx["os"]],
            )
            if envs.count() != 0:
                sys.exit(
                    "Trying to create new environment, but environment with no dependencies exists (this should not happen)"
                )

            # For kernel, note that we aren't adding kernel_version (too much detail)
            # Create the environment
            env, _ = Environment.objects.get_or_create(
                hostname=run[idx["hostname"]],
                arch=run[idx["arch"]],
                kernel=run[idx["kernel"]],
                host_os=run[idx["os"]],
            )
            env.dependencies.add(dep)
            env.save()
        else:
            env = envs[0]

        # Create repository states (we do not have history)
        dyninst_repo, _ = RepositoryState.objects.get_or_create(
            name="https://github.com/dyninst/dyninst",
            commit=run[idx["dyninst_commit"]],
            branch=run[idx["dyninst_branch"]],
        )
        testsuite_repo, _ = RepositoryState.objects.get_or_create(
            name="https://github.com/dyninst/testsuite",
            commit=run[idx["testsuite_commit"]],
            branch=run[idx["testsuite_branch"]],
        )

        # Create the build results (we don't know num jobs or time)
        # QUESTION: does this assume the same results file for legacy?
        # We will need a function that can handle passing the legacy log to log field if it exists
        # NOTE that I'm putting the log here so that the builds are unique (otherwise will be shared based on status)
        dyninst_build, _ = BuildResult.objects.get_or_create(
            status=run[idx["dyninst_build_status"]], legacy_log=run[idx["upload_file"]]
        )
        testsuite_build, _ = BuildResult.objects.get_or_create(
            status=run[idx["tests_build_status"]], legacy_log=run[idx["upload_file"]]
        )

        # Now create the test run result!
        # We don't know single step, parallel tests, threads, or time
        test_run_result, _ = TestRunResult.objects.get_or_create(
            dyninst_build=dyninst_build,
            testsuite_build=testsuite_build,
            test_run_status=run[idx["tests_run_status"]],
            legacy_log=run[idx["upload_file"]],
        )

        # Create a compiler if needed (note this can be Unknown)
        compiler, _ = Compiler.objects.get_or_create(
            name=run[idx["compiler_name"]], version="Unknown"
        )

        # Datetime converted from string
        date_run = make_aware(parse_datetime(run[idx["run_date"]]))

        # Now create the testrun and keep track of the lookup
        # NOTE: we don't have any commands here!
        test_run, _ = TestRun.objects.get_or_create(
            date_run=date_run,
            dyninst=dyninst_repo,
            testsuite=testsuite_repo,
            environment=env,
            pull_request=pr,
            cirun_url="unknown",
            compiler=compiler,
            result=test_run_result,
        )
        test_run_lookup[run[idx["id"]]] = test_run.id

        # Query for the test results
        test_results = conn.run_query(
            "SELECT * FROM test_result WHERE runid=%s;" % run[idx["id"]]
        )
        for result in test_results:

            # Get the test mode
            test_mode = TestMode.objects.get(name=result[ridx["mode"]])

            # prepare booleans
            pic = False if result[ridx["pic"]] == "nonPIC" else True
            is64bit = False if result[ridx["abi"]] == "32" else True
            dynamic = True if result[ridx["link"]] == "dynamic" else False

            # Get the compiler again!
            compiler, _ = Compiler.objects.get_or_create(
                name=result[ridx["compiler"]], version="Unkown"
            )
            test_result, _ = TestResult.objects.get_or_create(
                run=test_run,
                name=result[ridx["test_name"]],
                compiler=compiler,
                test_mode=test_mode,
                isPIC=pic,
                is64bit=is64bit,
                isDynamic=dynamic,
                reason=result[ridx["reason"]],
                optimization=result[ridx["optimization"]],
                status=result[ridx["result"]],
                threading=result[ridx["threading"]],
            )
            test_result_lookup[result[ridx["resultid"]]] = test_result.id

    return test_run_lookup, test_result_lookup
