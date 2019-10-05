import sql.test_results
import sql.runs

def summary(db, runid):
    summary = {}
    summary.setdefault('TOTAL', 0)
    for k,v in sql.test_results.summary(db, runid):
        summary.setdefault(k, v)
        summary['TOTAL'] += v
    return summary

def get(db, runid, result=None):
    run = sql.runs.get(db, runid=runid)
    
    if run is None or len(run) == 0:
        return None
    
    results = sql.test_results.get(db, runid, result)
    
    if results is None or len(results) == 0:
        return None
    
    res = {
        'run': run[0],
        'result_type': result,
        'results': results
    }
    
    return res
