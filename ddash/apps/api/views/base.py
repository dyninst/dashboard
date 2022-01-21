from django.conf import settings

from ratelimit.mixins import RatelimitMixin

from ddash.settings import cfg
from ddash.version import __version__
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


class ServiceInfo(RatelimitMixin, APIView):
    """Return a 200 response to indicate a running service, along with
    metadata about the service. This is similar to https://ga4gh.github.io/,
    but not for a workflow so only a subset of fields.
    """

    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "GET"
    renderer_classes = (JSONRenderer,)

    def get(self, request):
        print("GET /")

        data = {
            "id": "ddash",
            "status": "running",
            "name": "Dyninst Dashboard (ddash)",
            "description": "This service provides a dashboard for Dyninst results",
            "organization": {"name": "dyninst", "url": "https://github.com/dyninst"},
            "contactUrl": cfg.HELP_CONTACT_URL,
            "documentationUrl": "https://github.com/dyninst/dashboard",
            "createdAt": settings.SERVER_CREATION_DATE,
            "updatedAt": cfg.UPDATED_AT,
            "environment": cfg.ENVIRONMENT,
            "version": __version__,
            "auth_instructions_url": "OAauth2 is currently disabled.",
        }

        # Must make model json serializable
        return Response(status=200, data=data)
