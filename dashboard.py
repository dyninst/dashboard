import sys
import bottle
import regressions
import runs
from sql.bottle_sqlite import SQLitePlugin

sqlite = SQLitePlugin(dbfile="results.sqlite3")
bottle.install(sqlite)

# This is here to allow running under the built-in bottle server
base_url = ''

@bottle.route('/regressions')
def show_regressions(db):
    cur_id = bottle.request.query.id
    try:
        regs = regressions.by_arch(db, cur_id)
    except:
        msg = str(sys.exc_info()[1])
        raise bottle.HTTPError(500, 'Error calculating regressions: {0:s}'.format(msg))
    return bottle.template('regressions', regs=regs, base_url=base_url)

@bottle.route('/')
def index(db):
    try:
        res = runs.most_recent(db)
    except:
        msg = str(sys.exc_info()[1])
        raise bottle.HTTPError(500, 'Error getting runs: {0:s}'.format(msg))

    return bottle.template('runs', runs=res, base_url=base_url)

@bottle.route('/logs/<filename:path>')
def download(filename):
    return bottle.static_file(filename, root='logs/', download=filename)

@bottle.route('/upload')
def show_upload_form():
    return bottle.template('upload', base_url=base_url)

@bottle.route('/upload', method='POST')
def process_upload(db):
    user_file = bottle.request.files.get('upload')
    try:
        runs.upload(db, user_file)
    except:
        msg = str(sys.exc_info()[1])
        raise bottle.HTTPError(500, 'Error processing upload: {0:s}'.format(msg))
    
    return bottle.redirect(base_url)

if __name__ == '__main__':
    bottle.run(host='localhost', port=8080)
else:
    base_url = bottle.default_app().get_url('/')
