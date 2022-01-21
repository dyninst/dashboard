from django.conf import settings
from django.urls import reverse
from django.db.models import Count, Case, When, IntegerField, Q, Subquery, OuterRef

from ratelimit.mixins import RatelimitMixin

from ddash.apps.main.models import TestRun, Dependency
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


class ResultsTable(RatelimitMixin, APIView):
    """server side render main index table"""

    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "GET"
    renderer_classes = (JSONRenderer,)

    def get(self, request, year=None):
        print("GET BuildsTable")

        # Start and length to return
        start = int(request.GET["start"])
        length = int(request.GET["length"])
        draw = int(request.GET["draw"])
        query = request.GET.get("search[value]", "")
        queryset = TestRun.objects.all()

        # A tag page should filter to those tags
        tag = request.GET.get("tag")
        if tag:
            queryset = queryset.filter(tags__name=tag)

        # Annotate with libc version
        queryset = queryset.annotate(
            libc_version=Subquery(
                Dependency.objects.filter(
                    id=OuterRef("environment__dependencies__id"), name="libc"
                ).values("name")
            )
        )

        # First do the search to reduce the size of the set
        if query:
            queryset = queryset.filter(
                Q(date_run__icontains=query)
                | Q(environment__arch__icontains=query)
                | Q(environment__hostname__icontains=query)
                | Q(environment__host_os__icontains=query)
                | Q(compiler__name__icontains=query)
                | Q(compiler__version__icontains=query)
                | Q(environment__dependencies__name__icontains=query)
                | Q(environment__dependencies__version__icontains=query)
                | Q(result__testsuite_build__status__icontains=query)
                | Q(result__dyninst_build__status__icontains=query)
                | Q(dyninst__branch__icontains=query)
                | Q(dyninst__commit__icontains=query)
                | Q(testsuite__branch__icontains=query)
                | Q(testsuite__commit__icontains=query)
            )

        # Order column and direction
        order = request.GET["order[0][column]"]
        direction = request.GET["order[0][dir]"]  # asc or desc
        order_lookup = {
            "0asc": "id",
            "0desc": "-id",
            "1asc": "date_run",
            "1desc": "-date_run",
            "2asc": "environment__arch",
            "2desc": "-environment__arch",
            "3asc": "environment__hostname",
            "3desc": "-environment__hostname",
            "6asc": "compiler__name",
            "6desc": "-compiler__name",
            "7asc": "libc_version",
            "7desc": "-libc_version",
            "8asc": "result__dyninst_build__status",
            "8desc": "-result__dyninst_build__status",
            "9asc": "result__testsuite_build__status",
            "9desc": "-result__testsuite_build__status",
        }

        # Empty datatable
        data = {"draw": draw, "recordsTotal": 0, "recordsFiltered": 0, "data": []}
        count = 0

        order_by = "%s%s" % (order, direction)
        if order_by in order_lookup:
            print(f"Ordering by {order_by}")
            queryset = queryset.order_by(order_lookup[order_by])
            count = queryset.count()

        if start > count:
            start = 0
        end = start + length - 1

        # If we've gone too far
        if end > count:
            end = count - 1

        queryset = queryset[start : end + 1]
        data["recordsTotal"] = count
        data["recordsFiltered"] = count

        # Annotate with result counts
        queryset = queryset.annotate(
            tests_failed=Count("testresult_set__status" == "FAILED"),
            tests_passed=Count("testresult_set__status" == "PASSED"),
            tests_crashed=Count("testresult_set__status" == "CRASHED"),
            tests_hanged=Count("testresult_set__status" == "HANGED"),
            tests_skipped=Count("testresult_set__status" == "SKIPPED"),
        )

        for run in queryset:

            # Logic dictated by @thaines!
            result_text = "PASSED"
            regressions_count = run.regressions_current_run.count()
            if regressions_count > 0:
                result_text = "regressions " + regressions_count
            else:
                error_count = run.testresult_set.filter(
                    status__in=["FAILED", "CRASHED", "HANGED"]
                ).count()
                if error_count > 0:
                    result_text = "fail/crash/hang " + error_count

            dyninst_text = "<a href='%s'>%s</a>" % (
                run.dyninst.name,
                run.dyninst.branch,
            )
            testsuite_text = "<a href='%s'>%s</a>" % (
                run.testsuite.name,
                run.testsuite.branch,
            )
            if run.cirun_url:
                dyninst_text = "<a href='%s'>%s</a>" % (
                    run.cirun_url,
                    run.pull_request.pr_id,
                )
                testsuite_text = dyninst_text
            elif run.pull_request is not None:
                dyninst_text = "<a href='%s'>%s</a>" % (
                    run.pull_request.url,
                    run.pull_request.pr_id,
                )
                testsuite_text = dyninst_text

            data["data"].append(
                [
                    '<div style="float: left; margin: 0px 4px;">%s</div>' % run.id,
                    '<div style="float: left; margin: 0px 4px;">%s</div>'
                    % run.date_run,
                    run.environment.hostname,
                    '<div style="float: left; margin: 0px 4px;">%s</div>'
                    % run.environment.arch,
                    run.compiler.name + " " + run.compiler.version
                    if run.compiler.version
                    else "",
                    run.result.dyninst_build.status,
                    run.result.testsuite_build.status,
                    result_text,
                    dyninst_text,
                    testsuite_text,
                    # Extra shown in drop down
                    run.compiler.name,
                    run.compiler.version,
                    run.compiler.path,
                    run.dyninst.name,
                    run.dyninst.commit,
                    run.dyninst.branch,
                    run.testsuite.name,
                    run.testsuite.commit,
                    run.testsuite.branch,
                    run.tests_failed,
                    run.tests_passed,
                    run.tests_crashed,
                    run.tests_hanged,
                    run.tests_skipped,
                ]
            )

        return Response(status=200, data=data)
