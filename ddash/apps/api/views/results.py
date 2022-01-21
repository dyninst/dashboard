from django.conf import settings
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.urls import reverse

from ratelimit.decorators import ratelimit
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from ddash.settings import cfg
from ddash.apps.main.tasks import import_result
from rest_framework.response import Response
from rest_framework.views import APIView

from ..auth import is_authenticated

import json


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
        print(data)

        # We require the spack version and the spec
        result = import_result(data.get("result"))
        return Response(status=result["code"], data=result)
