import sql.views

def by_arch(db, cur_id):
    """
        Compare the run specified by `cur_id` against the most
        recent run on the same host
    """
    regs = {}
    cur_run = sql.views.runs(db, runid=cur_id)[0]
    regs.setdefault('base_commit', cur_run)
    
    regs['against_arch'] = []
    hosts = sql.views.run_hosts(db, arch=cur_run['arch'])
    
    for row in hosts:
        run = sql.views.most_recent_run(db, cur_id, hostname=row['hostname'])[0]
        d = {'run': run, 'regressions':None}
        regressions = sql.views.regressions(db, cur_id, run['id'])
        if len(regressions) > 0:
            d['regressions'] = regressions
        regs['against_arch'].append(d)
    
    return regs
