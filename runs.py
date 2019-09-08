import sys
import sql.runs
import sql.regressions
import test_results
import io
import log_files
import tarfile
import csv

def _process_runs(runs, db):
    res = []
    if len(runs) > 0:
        cols = runs[0].keys()
        for r in runs:
            d = dict(zip(cols,r))
            runid = r['id']
            d.setdefault('runid', runid)
            d.setdefault('summary', d['tests_run_status'])
            d.setdefault('regressions', '--')
            
            if d['tests_run_status'] == 'OK':
                res_summary = test_results.summary(db, runid)
                if res_summary['TOTAL'] > 0:
                    d['summary'] = \
                        str(res_summary['PASSED'])  + '/' + \
                        str(res_summary['FAILED'])  + '/' + \
                        str(res_summary['SKIPPED']) + '/' + \
                        str(res_summary['CRASHED']) + '  (' + \
                        str(res_summary['TOTAL'])   + ')'
                
                d['regressions'] = sql.regressions.counts(db, runid)
                if d['regressions'] == 0:
                    d['regressions'] = 'none'
            res.append(d)
    return res

def most_recent(db):
    runs = sql.runs.get(db, limit=20, order_by='run_date')
    return _process_runs(runs, db)

def by_commit(db, commit):
    runs = sql.runs.get_by_commit(db, commit)
    return _process_runs(runs, db)

def by_branch(db, branch):
    runs = sql.runs.get_by_branch(db, branch)
    return _process_runs(runs, db)

def upload(db, user_file):
    if user_file is None:
        raise RuntimeError("Uploaded file is not valid")

    # Save the uploaded file
    # NB: This needs to be done _before_ it is read from
    from uuid import uuid4
    file_name = str(uuid4()) + '.tar.gz'
    user_file.save('logs/' + file_name)

    try:
        with tarfile.open(fileobj=user_file.file, mode="r:gz") as tar:
            files = [m.name for m in tar.getmembers()]
            
            if "build.log" not in files:
                raise RuntimeError("No build log found")
    
            logfile = tar.extractfile("build.log")
            results = log_files.read_properties(io.TextIOWrapper(logfile, encoding='utf-8'))
            
            # Split the architecture and vendor names
            arch, vendor = results['arch'].split('/', 1)
            results['arch'] = arch
            results.setdefault('vendor', vendor)
            
            # Save the log file name
            results['user_file'] = file_name

            # Determine the status of the Dyninst build
            if "{0:s}/dyninst/Build.FAILED".format(results['root_dir']) in files:
                results['dyninst_build_status'] = 'FAILED'
            else:
                results['dyninst_build_status'] = 'OK'
            
            # Determine the status of the Testsuite build
            if "{0:s}/testsuite/Build.FAILED".format(results['root_dir']) in files:
                results['tests_build_status'] = 'FAILED'
            elif "{0:s}/testsuite/build/build.out".format(results['root_dir']) not in files:
                results['tests_build_status'] = 'not built'
            else:
                results['tests_build_status'] = 'OK'
            
            # Determine the status of the Testsuite run
            results_log_filename = "{0:s}/testsuite/tests/results.log".format(results['root_dir'])
            if "{0:s}/Tests.FAILED".format(results['root_dir']) in files:
                results['tests_run_status'] = 'FAILED'
            elif results_log_filename not in files:
                results['tests_run_status'] = 'not run'
            else:
                results['tests_run_status'] = 'OK'
            
            # Read the git branches and commits
            results.update(log_files.read_git_logs(tar, results['root_dir'], files))
            
            # There may be a trailing period in the UTC date
            # Sqlite doesn't like that, so remove it
            results['date'] = results['date'].replace('.', '')

            # Gather compiler information
            results.update(log_files.read_compiler_logs(tar, results['root_dir'], files))

            # Save the run information
            try:
                runid = sql.runs.create(db, results)
            except:
                e = sys.exc_info()[0]
                raise RuntimeError("Error creating run: {0:s}".format(e))
            
            # Load the results into the database
            if results['dyninst_build_status'] == 'OK' and \
               results['tests_build_status'] == 'OK' and \
               results['tests_run_status'] == 'OK':
                try:
                    logfile = tar.extractfile(results_log_filename)
                    reader = csv.reader(io.TextIOWrapper(logfile, encoding='utf-8'))
                    next(reader) # skip the header
                    sql.test_results.bulk_insert(db, runid, reader)
                except:
                    e = str(sys.exc_info()[0])
                    raise RuntimeError("Error inserting test_results: {0:s}".format(e))
    except(tarfile.ReadError):
        from os import unlink
        unlink('logs/' + file_name)
        raise RuntimeError("'{0:s}' is not a valid tarfile".format(user_file.filename))
