import sql.views.regressions

def by_arch(db, cur_id):
    """
        Compare the run specified by `cur_id` against the most
        recent runs on the same architecture
    """
    regs = {}
    cur_run = sql.views.runs.runs(db, runid=cur_id)[0]
    regs.setdefault('base_commit', cur_run)
    
    regs['results'] = []
    prev_runs = sql.views.runs.most_recent_runs_by_arch(db, cur_id)
    
    for r in prev_runs:
        d = {'run': r, 'regressions':None}
        regressions = sql.views.regressions.by_arch(db, cur_id, r['id'])
        if len(regressions) > 0:
            d['regressions'] = regressions
        regs['results'].append(d)
    
    return regs
