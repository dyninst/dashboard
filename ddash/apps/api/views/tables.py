from django.conf import settings
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.db.models import (
    Count,
    Case,
    When,
    IntegerField,
    Q,
    Subquery,
    OuterRef,
    Value,
    CharField,
)
from ratelimit.mixins import RatelimitMixin

from ddash.apps.main.models import TestRun, Dependency
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


class ResultsDetailTable(RatelimitMixin, APIView):
    """server side render of detailed results"""

    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "GET"
    renderer_classes = (JSONRenderer,)

    def get(self, request, year=None):
        print("GET ResultsDetailTable")

        # Start and length to return
        start = int(request.GET["start"])
        length = int(request.GET["length"])
        draw = int(request.GET["draw"])
        query = request.GET.get("search[value]", "")
        queryset = TestRun.objects.all()
        run_id = request.GET.get("run_id")
        run = get_object_or_404(TestRun, id=run_id)
        queryset = run.testresult_set.all()

        # Annotate with strings for dynamic/static and 64bit/32bit and PIC/notPIC
        queryset = queryset.annotate(
            is_dynamic=Case(
                When(isDynamic=True, then=Value("dynamic")),
                default=Value("static"),
                output_field=CharField(),
            ),
            is_pic=Case(
                When(isPIC=True, then=Value("PIC")),
                default=Value("nonPIC"),
                output_field=CharField(),
            ),
            is_64bit=Case(
                When(is64bit=True, then=Value("64")),
                default=Value("32"),
                output_field=CharField(),
            ),
        )

        # First do the search to reduce the size of the set
        if query:
            queryset = queryset.filter(
                Q(id__icontains=query)
                | Q(name__icontains=query)
                | Q(compiler__name__icontains=query)
                | Q(compiler__version__icontains=query)
                | Q(optimization__icontains=query)
                | Q(is_64bit__icontains=query)
                | Q(test_mode__name__icontains=query)
                | Q(threading__icontains=query)
                | Q(is_dynamic__icontains=query)
                | Q(is_pic__icontains=query)
                | Q(reason__icontains=query)
                | Q(status__icontains=query)
            )

        # Order column and direction
        order = request.GET["order[0][column]"]
        direction = request.GET["order[0][dir]"]  # asc or desc
        order_lookup = {
            "0asc": "id",
            "0desc": "-id",
            "1asc": "name",
            "1desc": "-name",
            "2asc": "compiler__name",
            "2desc": "-compiler__name",
            "3asc": "optimization",
            "3desc": "-optimization",
            "4asc": "is_64bit",
            "4desc": "-is64bit",
            "5asc": "test_mode__name",
            "5desc": "-test_mode__name",
            "6asc": "threading",
            "6desc": "-threading",
            "7asc": "is_dynamic",
            "7desc": "-is_dynamic",
            "8asc": "is_pic",
            "8desc": "-is_pic",
            "9asc": "reason",
            "9desc": "-reason",
            "10asc": "status",
            "10desc": "-status",
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

        for run in queryset:
            compiler_name = (
                run.compiler.name
                if (run.compiler.name and run.compiler.name != "Unknown")
                else ""
            )
            compiler_name = (
                compiler_name + " " + run.compiler.version
                if (run.compiler.version and run.compiler.version != "Unknown")
                else ""
            )
            data["data"].append(
                [
                    '<div style="float: left; margin: 0px 4px;">%s</div>' % run.id,
                    run.name,
                    compiler_name,
                    run.optimization,
                    run.is_64bit,
                    run.test_mode.name,
                    run.threading,
                    run.is_dynamic,
                    run.is_pic,
                    run.reason,
                    run.status,
                ]
            )

        return Response(status=200, data=data)


class ResultsTable(RatelimitMixin, APIView):
    """server side render main index table"""

    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "GET"
    renderer_classes = (JSONRenderer,)

    def get(self, request, year=None):
        print("GET ResultsTable")

        # Start and length to return
        start = int(request.GET["start"])
        length = int(request.GET["length"])
        draw = int(request.GET["draw"])
        query = request.GET.get("search[value]", "")
        queryset = TestRun.objects.all()

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
            "2asc": "environment__hostname",
            "2desc": "-environment__hostname",
            "3asc": "environment__arch",
            "3desc": "-environment__arch",
            "4asc": "compiler__name",
            "4desc": "-compiler__name",
            "5asc": "result__dyninst_build__status",
            "5desc": "-result__dyninst_build__status",
            "6asc": "result__testsuite_build__status",
            "6desc": "-result__testsuite_build__status",
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
                result_text = "regressions " + str(regressions_count)
            else:
                error_count = run.testresult_set.filter(
                    status__in=["FAILED", "CRASHED", "HANGED"]
                ).count()
                if error_count > 0:
                    result_text = "ERRORS " + str(error_count)

            run_url = reverse("main:testrun_detail", args=[run.id])
            data["data"].append(
                [
                    '<div style="float: left; margin: 0px 4px;"><a href="%s">%s</a></div>'
                    % (run_url, run.id),
                    '<div style="float: left; margin: 0px 4px;">%s</div>'
                    % run.date_run,
                    run.environment.hostname,
                    '<div style="float: left; margin: 0px 4px;">%s</div>'
                    % run.environment.arch,
                    run.get_compiler_name(),
                    run.result.dyninst_build.status,
                    run.result.testsuite_build.status,
                    result_text,
                    run.get_dyninst_text(),
                    run.get_testsuite_text(),
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
