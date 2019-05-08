from bottle import route, run, request, HTTPError, template, static_file
import tarfile
import sqlite3
from io import TextIOWrapper

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
            results = read_properties(TextIOWrapper(logfile, encoding='utf-8'))
    
            root_dir = results['root_dir']
            if "{0:s}/FAILED".format(root_dir) in files:
                results['build_status'] = 'FAILED'
            else:
                results['build_status'] = 'OK'
            
            # Read the git branches and commits
            results.update(read_git_logs(tar, root_dir, files))
                
        from uuid import uuid4
        file_name = 'logs/' + str(uuid4()) + '.tar.gz'
        user_file.save(file_name)
        results['user_file'] = file_name
        
        return template('upload_results', results=results)
    
    except(tarfile.ReadError):
        raise HTTPError(500, body="'{0:s}' is not a valid tarfile".format(user_file.filename))

def read_git_logs(tar, root_dir, tar_files):
    res = {}
    for d in ('dyninst','testsuite'):
        logfile = "{0:s}/{1:s}/git.log".format(root_dir, d)
        if logfile in tar_files:
            git_log = tar.extractfile(logfile)
            git_results = read_properties(TextIOWrapper(git_log, encoding='utf-8'))
            res['{0:s}_branch'.format(d)] = git_results['branch']
            res['{0:s}_commit'.format(d)] = git_results['commit']
        else:
            res['{0:s}_branch'.format(d)] = 'Unknown'
            res['{0:s}_commit'.format(d)] = 'Unknown'
    return res

def read_properties(file):
    props = {}
    for l in file:
        if ': ' in l:
            k, v = l.split(': ')
            if k is not None:
                props[k] = str.strip(v)
    return props


if __name__ == '__main__':
    run(host='localhost', port=8080)
