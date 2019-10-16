import sys
import bottle
import regressions
import runs
import test_results
from sql.bottle_sqlite import SQLitePlugin

sqlite = SQLitePlugin(dbfile="results.sqlite3")
bottle.install(sqlite)

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
        regs = regressions.by_arch(db, cur_id)
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

if __name__ == '__main__':
    bottle.run(host='localhost', port=8080)
