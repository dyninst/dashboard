from io import TextIOWrapper
from os.path import split as path_split

def read_compiler_logs(tar, root_dir, tar_files):
    res = {
        'compiler': {
            'dyninst': {
                'c': {
                    'path': '',
                    'name': 'Unknown',
                    'version': ''
                },
                'cxx': {
                    'path': '',
                    'name': 'Unknown',
                    'version': ''
                }
            },
            'testsuite': {
                'c': {
                    'path': '',
                    'name': 'Unknown',
                    'version': ''
                },
                'cxx': {
                    'path': '',
                    'name': 'Unknown',
                    'version': ''
                }
            }
        }}
    for d in ('dyninst', 'testsuite'):
        logfile = "{0:s}/{1:s}/build/compilers.conf".format(root_dir, d)
        if logfile in tar_files:
            compiler_log = tar.extractfile(logfile)
            compiler_results = read_properties(TextIOWrapper(compiler_log, encoding='utf-8'))
            for lang in ('c', 'cxx'):
                path = compiler_results['{0:s}_path'.format(lang)]
                (dir_name, base) = path_split(path)
                res['compiler'][d][lang]['path'] = dir_name
                res['compiler'][d][lang]['name'] = base
                res['compiler'][d][lang]['version'] = compiler_results['{0:s}_version'.format(lang)]
    return res

def read_git_logs(tar, root_dir, tar_files):
    res = {}
    for d in ('dyninst', 'testsuite'):
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
            k, v = l.split(': ', 1)
            if k is not None:
                props[k] = str.strip(v)
    return props
