import sql.test_results
import sql.runs

def summary(db, runid):
    summary = {}
    
    names = ['PASSED','FAILED','SKIPPED','CRASHED','HANGED']
    res = sql.test_results.counts(db, runid)
    
    for n,c in zip(names, res[0]):
        summary[n] = c

    summary['TOTAL'] = sum(summary.values())

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
