from bottle import route, run, request, HTTPError, template, static_file
import tarfile
from io import TextIOWrapper
import log_files
import sql.inserts
import sql.views

@route('/logs/<filename:path>')
def download(filename):
    return static_file(filename, root='logs/', download=filename)

@route('/upload')
def show_upload_form():
    return template('upload')

@route('/upload', method='POST')
def process_upload():
    user_file = request.files.get('upload')

    try:
        with tarfile.open(fileobj=user_file.file, mode="r:gz") as tar:
            files = [m.name for m in tar.getmembers()]
            
            if "build.log" not in files:
                raise HTTPError(500, body="No build.log in {0:s}".format(user_file.filename))
    
            logfile = tar.extractfile("build.log")
            results = log_files.read_properties(TextIOWrapper(logfile, encoding='utf-8'))
            
            from uuid import uuid4
            file_name = 'logs/' + str(uuid4()) + '.tar.gz'
            user_file.save(file_name)
            results['user_file'] = file_name
    
            root_dir = results['root_dir']
            if "{0:s}/FAILED".format(root_dir) in files:
                results['build_status'] = 'FAILED'
            else:
                results['build_status'] = 'OK'
            
            # Read the git branches and commits
            results.update(log_files.read_git_logs(tar, root_dir, files))
            
            # Load the results into the database
            if results['build_status'] == 'OK':
                logfile_name = "{0:s}/testsuite/tests/results.log".format(root_dir)
                if logfile_name not in files:
                    results['summary'] = None
                else:
                     try:
                        runid = sql.inserts.create_run(results)
                        logfile = tar.extractfile(logfile_name)
                        sql.inserts.save_results(runid, TextIOWrapper(logfile, encoding='utf-8'))
                     except:
                         raise HTTPError(500, body="Error creating run for {0:s}".format(user_file.filename))
        
        return template('upload_results', results=results)
    
    except(tarfile.ReadError):
        raise HTTPError(500, body="'{0:s}' is not a valid tarfile".format(user_file.filename))

if __name__ == '__main__':
    run(host='localhost', port=8080)
