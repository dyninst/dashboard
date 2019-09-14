import sql.regressions
import sql.runs

def by_arch(db, cur_id):
    """
        Compare the run specified by `cur_id` against the most
        recent runs on the same architecture
    """
    regs = {}
    cur_run = sql.runs.get(db, runid=cur_id)[0]
    regs.setdefault('base_commit', cur_run)

    regs['results'] = []
    regs['type'] = 'arch'
    prev_runs = sql.runs.most_recent_by_arch(db, cur_id)

    for r in prev_runs:
        d = {'run': r, 'regressions':None}
        regressions = sql.regressions.get(db, cur_id, r['id'])
        if len(regressions) > 0:
            d['regressions'] = regressions
        regs['results'].append(d)

    return regs

def by_run(db, cur_id, prev_id):
    """
        Compare the run specified by `cur_id` against
        the run specified by `prev_id`.
    """
    regs = {}
    regs['type'] = 'run'
    regs['base_commit'] = sql.runs.get(db, runid=cur_id)[0]

    # The bottle template expects a list of dictionaries, even though
    # there is only one entry in this case.
    regs['results'] = [
        {
            'run': sql.runs.get(db, runid=prev_id)[0],
            'regressions': sql.regressions.get(db, cur_id, prev_id)
        }
    ]

    return regs
