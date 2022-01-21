from django.shortcuts import render, get_object_or_404

from ddash.apps.main.models import TestRun

from ratelimit.decorators import ratelimit
from ddash.settings import (
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
)

import difflib
import json


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def spec_diff(request, spec1=None, spec2=None):
    """
    Allow the user to select two specs to diff.
    """
    specs = Spec.objects.all().order_by("name")
    if not spec1 or not spec2:
        return render(request, "specs/diff.html", {"specs": specs})

    spec1 = get_object_or_404(Spec, pk=spec1)
    spec2 = get_object_or_404(Spec, pk=spec2)
    diff1 = json.dumps(spec1.to_dict(), indent=4).split("\n")
    diff2 = json.dumps(spec2.to_dict(), indent=4).split("\n")
    diff = difflib.HtmlDiff().make_table(diff1, diff2)
    return render(
        request,
        "specs/diff.html",
        {"specs": specs, "diff": diff, "spec1": spec1, "spec2": spec2},
    )


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def testrun_detail(request, id):
    testrun = get_object_or_404(TestRun, pk=id)
    return render(
        request,
        "runs/detail.html",
        {"testrun": testrun},
    )
