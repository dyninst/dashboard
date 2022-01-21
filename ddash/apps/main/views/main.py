from django.shortcuts import render, get_object_or_404
from ddash.apps.main.models import TestRun

from ratelimit.decorators import ratelimit
from ddash.settings import (
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
)

# Dashboard


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def index(request):
    builds = TestRun.objects.all()
    return render(request, "main/index.html", {"builds": builds})


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def builds_by_tag(request, tag):
    builds = Build.objects.filter(tags__name=tag)
    # Present all tags for browsing
    tags = Build.objects.all().values_list("tags__name", flat=True).distinct()
    return render(
        request, "main/index.html", {"builds": builds, "tag": tag, "tags": tags}
    )


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def builds_by_owner(request, username):
    builds = Build.objects.filter(owner__username=username)
    tags = builds.values_list("tags__name", flat=True).distinct()
    return render(
        request, "main/index.html", {"builds": builds, "owner": username, "tags": tags}
    )


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def build_detail(request, bid):
    build = get_object_or_404(Build, pk=bid)

    # Generate BuildWarnings and BuildErrors if don't exist
    if build.logs_parsed == 0:
        parse_build_logs(build)
    return render(request, "builds/detail.html", {"build": build})


"""
@bottle.route('/details')
def dummy_details(db):
    raise bottle.HTTPError(400)

@bottle.route('/details/<runid>')
def show_details(db, runid):
    try:
        res = runs.details(db, runid)
    except:
        msg = str(sys.exc_info()[1])
        raise bottle.HTTPError(500, 'Error fetching run details: {0:s}'.format(msg))
    return bottle.template('details', results=res, url=bottle.url)

@bottle.route('/results')
def dummy_results(db):
    raise bottle.HTTPError(400)

@bottle.route('/results/<result_type>/<runid>')
def show_test_results(db, result_type, runid):
    try:
        res = test_results.get(db, runid, result=result_type)
    except:
        msg = str(sys.exc_info()[1])
        raise bottle.HTTPError(500, 'Error fetching test results: {0:s}'.format(msg))
    return bottle.template('test_results', results=res, url=bottle.url)

@bottle.route('/hostname/<name>')
def show_hostname(db, name):
    try:
        res = runs.by_hostname(db, name)
    except:
        msg = str(sys.exc_info()[1])
        raise bottle.HTTPError(500, 'Error getting runs: {0:s}'.format(msg))
    return bottle.template('runs', runs=res, url=bottle.url)

@bottle.route('/')
def index(db):
    try:
        res = runs.most_recent(db)
    except:
        msg = str(sys.exc_info()[1])
        raise bottle.HTTPError(500, 'Error getting runs: {0:s}'.format(msg))

    return bottle.template('runs', runs=res, url=bottle.url)

@bottle.route('/commit/<commit_id>')
def show_commit(db, commit_id):
    try:
        res = runs.by_commit(db, commit_id)
    except:
        msg = str(sys.exc_info()[1])
        raise bottle.HTTPError(500, 'Error getting runs for commit {0:s}:'.format(commit_id, msg))
    return bottle.template('runs', runs=res, url=bottle.url)

@bottle.route('/branch/<branch_name>')
def show_branch(db, branch_name):
    try:
        res = runs.by_branch(db, branch_name)
    except:
        msg = str(sys.exc_info()[1])
        raise bottle.HTTPError(500, 'Error getting runs for branch {0:s}:'.format(branch_name, msg))
    return bottle.template('runs', runs=res, url=bottle.url)

@bottle.route('/regressions')
def show_regressions(db):
    cur_id = bottle.request.query.id
    
    if cur_id is None:
        raise bottle.HTTPError(400, 'Invalid query')
    
    try:
        regs = regressions.by_host(db, cur_id)
    except:
        msg = str(sys.exc_info()[1])
        raise bottle.HTTPError(500, 'Error calculating regressions: {0:s}'.format(msg))
    return bottle.template('regressions', regs=regs, url=bottle.url)

@bottle.route('/regressions/run')
def show_regressions_by_host(db):
    cur_id = bottle.request.query.curid
    prev_id = bottle.request.query.previd
    
    if cur_id == '' or prev_id == '':
        raise bottle.HTTPError(400, 'Invalid query')
    
    try:
        regs = regressions.by_run(db, cur_id, prev_id)
    except:
        msg = str(sys.exc_info()[1])
        raise bottle.HTTPError(500, 'Error calculating regressions: {0:s}'.format(msg))
    return bottle.template('regressions', regs=regs, url=bottle.url)

@bottle.route('/logs')
@bottle.route('/logs/<filename:path>')
def download(filename):
    return bottle.static_file(filename, root='logs/', download=filename)

@bottle.route('/upload', method='POST')
def process_upload(db):
    user_file = bottle.request.files.get('upload')
    token = bottle.request.forms.get('token')

    try:
        runs.upload(db, user_file, token)
    except:
        msg = str(sys.exc_info()[1])
        raise bottle.HTTPError(500, 'Error processing upload: {0:s}'.format(msg))
    
    return bottle.redirect(bottle.url('/'))

@bottle.route('/search')
def search(db):
    try:
        args = {}
        query = bottle.request.query
        
        # Don't create args unless they are present in the query
        if query.since_date:
            args['since'] = query.since_date
        if query.before_date:
            args['before'] = query.before_date
        if query.dyninst_branch:
            args['dyninst_branch'] = query.dyninst_branch
        if query.testsuite_branch:
            args['testsuite_branch'] = query.testsuite_branch
        if query.dyninst_build_status:
            args['dyninst_build_status'] = query.dyninst_build_status
        if query.tests_build_status:
            args['tests_build_status'] = query.tests_build_status
        if query.tests_run_status:
            args['tests_run_status'] = query.tests_run_status
        if query.hostname:
            args['hostname'] = query.hostname
        if query.status:
            args['dyninst_build_status'] = query.status
            args['tests_build_status'] = query.status
            args['tests_run_status'] = query.status
        res = runs.search(db, args)
    except:
        msg = str(sys.exc_info()[1])
        raise bottle.HTTPError(500, 'Error searching: {0:s}'.format(msg))
    return bottle.template('runs', runs=res, url=bottle.url)

if __name__ == '__main__':
    bottle.run(host='localhost', port=8080)
"""