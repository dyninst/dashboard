from io import TextIOWrapper

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
