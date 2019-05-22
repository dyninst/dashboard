import bottle
from bottle import route, run, request, HTTPError, template, static_file, redirect
import tarfile
from io import TextIOWrapper
import log_files
import sql.inserts
import sql.views
from sql.bottle_sqlite import SQLitePlugin
import csv

sqlite = SQLitePlugin(dbfile="test.sqlite3")
bottle.install(sqlite)

@route('/')
def index(db):
    runs = sql.views.get_runs(db, limit=10, order_by='run_date')
    cols = runs[0].keys()
    res = []
    for r in runs:
        d = dict(zip(cols,r))
        runid = r[0]
        d.setdefault('summary', get_result_summary(db, runid))
        d.setdefault('regressions', 'Unknown')
        
        old_runid = sql.views.get_most_recent_run(db, runid, hostname=d['hostname'])
        old_runid = old_runid[0][0]
        if old_runid is not None:
            regs = sql.views.regressions(db, runid, old_runid)
            if regs:
                d['regressions'] = str(len(regs))
            else:
                d['regressions'] = 'none'
        res.append(d)
    return template('runs', runs=res)

@route('/logs/<filename:path>')
def download(filename):
    return static_file(filename, root='logs/', download=filename)

@route('/upload')
def show_upload_form():
    return template('upload')

@route('/upload', method='POST')
def process_upload(db):
    user_file = request.files.get('upload')
    
    if user_file is None:
        raise HTTPError(500, body="Uploaded file is not valid")

    # Save the uploaded file
    # NB: This needs to be done _before_ it is read from
    from uuid import uuid4
    file_name = 'logs/' + str(uuid4()) + '.tar.gz'
    user_file.save(file_name)

    try:
        with tarfile.open(fileobj=user_file.file, mode="r:gz") as tar:
            files = [m.name for m in tar.getmembers()]
            
            if "build.log" not in files:
                raise HTTPError(500, body="No build.log in {0:s}".format(user_file.filename))
    
            logfile = tar.extractfile("build.log")
            results = log_files.read_properties(TextIOWrapper(logfile, encoding='utf-8'))
            
            results['user_file'] = file_name
    
            root_dir = results['root_dir']
            if "{0:s}/FAILED".format(root_dir) in files:
                results['build_status'] = 'FAILED'
            else:
                results['build_status'] = 'OK'
            
            # Read the git branches and commits
            results.update(log_files.read_git_logs(tar, root_dir, files))
            
            # There may be a trailing period in the UTC date
            # Sqlite doesn't like that, so remove it
            results['date'] = results['date'].replace('.', '')

            # Save the run information
            try:
                runid = sql.inserts.create_run(db, results)
            except:
                raise HTTPError(500, body="Error creating run for {0:s}".format(user_file.filename))
            
            # Load the results into the database
            if results['build_status'] == 'OK':
                logfile_name = "{0:s}/testsuite/tests/results.log".format(root_dir)
                try:
                    logfile = tar.extractfile(logfile_name)
                    reader = csv.reader(TextIOWrapper(logfile, encoding='utf-8'))
                    next(reader) # skip the header
                    sql.inserts.save_results(db, runid, reader)
                except:
                    raise HTTPError(500, body="Error inserting results for {0:s}".format(user_file.filename))
        
        return redirect('/')
    
    except(tarfile.ReadError):
        from os import unlink
        unlink(file_name)
        raise HTTPError(500, body="'{0:s}' is not a valid tarfile".format(user_file.filename))

def get_result_summary(db, runid):
    try:                    
        summary = {}
        summary.setdefault('TOTAL', 0)
        for k,v in sql.views.results_summary(db, runid):
            summary.setdefault(k, v)
            summary['TOTAL'] += v
    except:
        raise HTTPError(500, body="Error creating summary")

    if summary['TOTAL'] > 0:
        return \
            str(summary['PASSED'])  + '/' + \
            str(summary['FAILED'])  + '/' + \
            str(summary['SKIPPED']) + '/' + \
            str(summary['CRASHED']) + '  (' + \
            str(summary['TOTAL'])   + ')'
    else:
        return 'Unknown'
    
    return summary

if __name__ == '__main__':
    run(host='localhost', port=8080)
