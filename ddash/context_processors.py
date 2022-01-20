from django.contrib.sites.shortcuts import get_current_site
from ddash import settings


def globals(request):
    return {
        "DYNINST_DASHBOARD_VERSION": settings.cfg.VERSION,
        "DOMAIN": settings.DOMAIN_NAME,
        "DOMAIN_NAME": settings.DOMAIN_NAME_PORTLESS,
        "GITHUB_REPOSITORY": settings.cfg.GITHUB_REPOSITORY,
        "GITHUB_DOCUMENTATION": settings.cfg.GITHUB_DOCUMENTATION,
        "SITE_NAME": get_current_site(request).name,
    }
