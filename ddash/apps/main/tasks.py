from ddash.apps.main.models import (
    TestRun,
    TestResult,
    TestMode,
    RepositoryState,
    PullRequest,
    Compiler,
    BuildResult,
    TestRunResult,
    TestResult,
)

import os

from ddash.apps.main.models import TestRun, RepositoryState, Environment, Dependency
import logging

logger = logging.getLogger(__name__)


def import_environment(data):
    """
    Get or create an environment.
    """
    # First deal with deps
    deps = []
    deps_ids = []
    for depname, depmeta in data.get("dependencies", {}).items():
        dep, _ = Dependency.objects.get_or_create(
            version=depmeta.get("version"), name=depname, path=depmeta.get("path")
        )

        # This is okay to do - never going to be a huge list
        deps.append(dep)
        deps_ids.append(dep.id)

    # Filter for exact match (deps are many to many and cannot be in unique constraint)
    environ = Environment.objects.filter(
        host_os=data.get("host_os"),
        hostname=data.get("hostname"),
        kernel=data.get("kernel"),
        arch=data.get("arch"),
        dependencies__id__in=deps_ids,
    )

    # We have an exact match, already created for these deps!
    if environ:
        return environ[0]

    environ = Environment(
        host_os=data.get("host_os"),
        hostname=data.get("hostname"),
        kernel=data.get("kernel"),
        arch=data.get("arch"),
    )
    environ.save()
    for dep in deps:
        environ.dependencies.add(dep)
    environ.save()
    return environ


def import_repository_state(repo):
    """
    Create a repository state, or return None if data not provided
    """
    repository, _ = RepositoryState.objects.get_or_create(
        name=repo.get("name"),
        commit=repo.get("commit"),
        branch=repo.get("branch"),
        history=repo.get("history"),
    )
    return repository


def import_pull_request(data):
    pr_id = int(data.get("pr_id")) if data.get("pr_id") else None
    pr, _ = PullRequest.objects.get_or_create(
        url=data.get("url"), user=data.get("user"), pr_id=pr_id
    )
    return pr


def import_compiler(data):
    compiler, _ = Compiler.objects.get_or_create(
        name=data.get("name"),
        version=data.get("version"),
        path=data.get("path"),
        language=data.get("language"),
    )
    return compiler


def import_test_run_result(data):
    """
    A test run result is a build result in the Json
    """
    # Create a build result for each of dyninst and testsuite
    dyninst = None
    testsuite = None
    for name, br in data.get("build_results", {}).items():

        time = int(br.get("time")) if br.get("time") else None
        num_jobs = int(br.get("num_jobs")) if br.get("num_jobs") else None

        if name == "dyninst":
            dyninst, _ = BuildResult.objects.get_or_create(
                status=br.get("status"), num_jobs=num_jobs, time=time
            )
        elif name == "testsuite":
            testsuite, _ = BuildResult.objects.get_or_create(
                status=br.get("status"), num_jobs=num_jobs, time=time
            )

    is_single_step = True if data.get("is_single_step") == "yes" else False
    threads = (
        int(data.get("num_parallel_tests")) if data.get("num_parallel_tests") else None
    )
    num_tests = (
        int(data.get("num_parallel_tests")) if data.get("num_parallel_tests") else None
    )
    threads = int(data.get("num_omp_threads")) if data.get("num_omp_threads") else None
    time = int(data.get("time")) if data.get("time") else None
    result = TestRunResult(
        dyninst_build=dyninst,
        testsuite_build=testsuite,
        test_run_status=data.get("test_run_status"),
        is_single_step=is_single_step,
        num_parallel_tests=num_tests,
        num_omp_threads=threads,
        time=time,
    )
    result.save()
    return result


def import_test_items(items, run):
    for item in items:
        # "aarch64_cft,,none,64,disk,NA,dynamic,nonPIC,PASSED",
        parts = item.split(",")
        if len(parts) != 10:
            print(
                "Warning, result should have N=10 parts, found %s: %s"
                % (len(parts), parts)
            )
            continue
        (
            name,
            compiler,
            optimization,
            is64Bit,
            test_mode,
            threading,
            dynamic,
            isPIC,
            status,
            reason,
        ) = parts

        test_mode, _ = TestMode.objects.get_or_create(
            name=test_mode.strip("'").strip('"')
        )
        compiler, _ = Compiler.objects.get_or_create(name=compiler)
        is64Bit = True if str(is64Bit) == "64" else False
        isPIC = True if isPIC and str(isPIC) == "nonPic" else False
        dynamic = True if dynamic and str(dynamic) == "dynamic" else False
        new_result = TestResult.objects.create(
            name=name,
            compiler=compiler,
            optimization=optimization,
            is64bit=is64Bit,
            test_mode=test_mode,
            isPIC=isPIC,
            threading=threading,
            isDynamic=dynamic,
            status=status,
            reason=reason,
            run=run,
        )


def import_result(data):
    """
    Create a new TestRun result
    """
    # First create repository metadata (dyninst and testsuite)
    repos = {}
    for name, repo in data.get("repositories", {}).items():
        repos[name] = import_repository_state(repo)

    # Create the environment
    environ = import_environment(data.get("environment"))

    # Create the pull request
    pr = import_pull_request(data.get("pull_request"))

    # Create the compiler
    compiler = import_compiler(data.get("compiler"))

    # Create the test run result
    result = import_test_run_result(data.get("test_run_results"))

    # Create a new test run
    test_run = TestRun(
        date_run=data["date_run"],
        dyninst=repos.get("dyninst"),
        testsuite=repos.get("testsuite"),
        environment=environ,
        pull_request=pr,
        cirun_url=data.get("cirun_url"),
        compiler=compiler,
        result=result,
    )
    test_run.save()

    # and then add items to it
    import_test_items(data.get("test_run_results", {}).get("items", []), test_run)

    data = {"test_run": test_run.id}
    return {"message": "success", "data": data, "code": 201}
