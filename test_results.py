import sql.test_results
import sql.runs

def summary(db, runid):
    summary = {}
    
    # We want a count for each possible status
    for row in sql.test_results.status_names(db):
        summary[row['name']] = 0
    summary['TOTAL'] = 0
    
    # Insert the actual counts (NB: not all possible statuses may be present)
    for name,count in sql.test_results.counts(db, runid):
        summary[name] = count
        summary['TOTAL'] += count
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
