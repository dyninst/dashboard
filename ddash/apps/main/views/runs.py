from django.shortcuts import render, get_object_or_404

from ddash.apps.main.models import TestRun

from ratelimit.decorators import ratelimit
from ddash.settings import (
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def testrun_detail(request, id):
    testrun = get_object_or_404(TestRun, pk=id)
    return render(
        request,
        "runs/detail.html",
        {"testrun": testrun},
    )
