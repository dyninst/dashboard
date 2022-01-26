from django.conf import settings
from django.db.models import F
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from ratelimit.decorators import ratelimit
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from ddash.settings import cfg
from ddash.apps.main.tasks import (
    import_result,
    import_test_log,
    import_build_log,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from ..auth import is_authenticated

import json


@csrf_exempt
def upload_log(request):

    # Acceptable log types
    log_types = ["test_log", "dyninst_build_log", "test_build_log"]

    # Both logs will be post with a log file
    if request.method == "POST" and request.FILES.get("logfile"):
        log_type = request.POST.get("log_type")
        run_id = request.POST.get("run_id")
        log_file = request.FILES["logfile"]

        # Both file_type and run_id are required
        if not log_type or not run_id:
            return JsonResponse(
                status=400, data={"message": "log_type and run_id are required"}
            )

        # We must recognize the log type!
        if log_type not in log_types:
            return JsonResponse(
                status=400,
                data={"message": "log_type must be one of %s" % ",".join(log_types)},
            )

        if log_type == "test_log":
            data = import_test_log(run_id, log_file)
        if log_type == "dyninst_build_log":
            data = import_build_log(run_id, log_file, "dyninst")
        if log_type == "test_build_log":
            data = import_build_log(run_id, log_file, "testsuite")
        return JsonResponse(status=data["code"], data=data)
    return JsonResponse(status=400, data={"message": "Malformed request."})


class NewTestResult(APIView):
    permission_classes = []
    allowed_methods = ("POST",)

    @method_decorator(
        ratelimit(
            key="ip",
            rate=settings.VIEW_RATE_LIMIT,
            method="POST",
            block=settings.VIEW_RATE_LIMIT_BLOCK,
        )
    )
    def post(self, request, *args, **kwargs):
        """POST /results/new/ to upload a json result"""

        # If allow_continue False, return response
        allow_continue, response, _ = is_authenticated(request)
        if not allow_continue:
            return response

        # Generate the config
        data = json.loads(request.body)

        # We require the spack version and the spec
        result = import_result(data.get("result"))
        return Response(status=result["code"], data=result)
