import sql.test_results

def summary(db, runid):
    summary = {}
    summary.setdefault('TOTAL', 0)
    for k,v in sql.test_results.summary(db, runid):
        summary.setdefault(k, v)
        summary['TOTAL'] += v
    return summary