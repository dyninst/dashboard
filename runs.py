import sys
import sql.views.runs
import sql.views.regressions
import sql.inserts
import io
import log_files
import tarfile
import csv

def most_recent(db):
    runs = sql.views.runs.runs(db, limit=10, order_by='run_date')
    res = []
    if len(runs) > 0:
        cols = runs[0].keys()
        for r in runs:
            d = dict(zip(cols,r))
            runid = r['id']
            d.setdefault('runid', runid)
            if d['tests_status'] == 'OK':
                summary = _result_summary(db, runid)
            else:
                summary = d['tests_status']
            
            d.setdefault('summary', summary)
            d.setdefault('regressions', 'Unknown')
            
            if d['tests_status'] == 'OK':
                d['regressions'] = sql.views.regressions.counts(db, runid)
                if d['regressions'] == 0:
                    d['regressions'] = 'none'
            res.append(d)
    return res

def _result_summary(db, runid):
    try:                    
        summary = {}
        summary.setdefault('TOTAL', 0)
        for k,v in sql.views.runs.results_summary(db, runid):
            summary.setdefault(k, v)
            summary['TOTAL'] += v
    except:
        raise "Error creating summary"

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

def upload(db, user_file):
    if user_file is None:
        raise "Uploaded file is not valid"

    # Save the uploaded file
    # NB: This needs to be done _before_ it is read from
    from uuid import uuid4
    file_name = str(uuid4()) + '.tar.gz'
    user_file.save('logs/' + file_name)

    try:
        with tarfile.open(fileobj=user_file.file, mode="r:gz") as tar:
            files = [m.name for m in tar.getmembers()]
            
            if "build.log" not in files:
                raise "No build log found"
    
            logfile = tar.extractfile("build.log")
            results = log_files.read_properties(io.TextIOWrapper(logfile, encoding='utf-8'))
            
            # Split the architecture and vendor names
            arch, vendor = results['arch'].split('/', 1)
            results['arch'] = arch
            results.setdefault('vendor', vendor)
            
            results['user_file'] = file_name
    
            root_dir = results['root_dir']
            
            for t in ('build','tests'):
                if "{0:s}/{1:s}.FAILED".format(root_dir, t.title()) in files:
                    results['{0:s}_status'.format(t)] = 'FAILED'
                else:
                    results['{0:s}_status'.format(t)] = 'OK'
            
            # Read the git branches and commits
            results.update(log_files.read_git_logs(tar, root_dir, files))
            
            # There may be a trailing period in the UTC date
            # Sqlite doesn't like that, so remove it
            results['date'] = results['date'].replace('.', '')

            # Save the run information
            try:
                runid = sql.inserts.create_run(db, results)
            except:
                e = sys.exc_info()[0]
                raise "Error creating run: {0:s}".format(e)
            
            # Load the results into the database
            if results['build_status'] == 'OK' and results['tests_status'] == 'OK':
                logfile_name = "{0:s}/testsuite/tests/results.log".format(root_dir)
                try:
                    logfile = tar.extractfile(logfile_name)
                    reader = csv.reader(io.TextIOWrapper(logfile, encoding='utf-8'))
                    next(reader) # skip the header
                    sql.inserts.save_results(db, runid, reader)
                except:
                    e = str(sys.exc_info()[0])
                    raise "Error inserting results: {0:s}".format(e)
    except(tarfile.ReadError):
        from os import unlink
        unlink(file_name)
        raise "'{0:s}' is not a valid tarfile".format(user_file.filename)
