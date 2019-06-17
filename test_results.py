import sql.test_results

def summary(db, runid):
    try:                    
        summary = {}
        summary.setdefault('TOTAL', 0)
        for k,v in sql.test_results.summary(db, runid):
            summary.setdefault(k, v)
            summary['TOTAL'] += v
    except:
        raise "Error creating summary"

    if summary['TOTAL'] > 0:
        return \
            str(summary['PASSED'])  + '/' + \
            str(summary['FAILED'])  + '/' + \
            str(summary['SKIPPED']) + '/' + \
            str(summary['CRASHED']) + '  (' + \
            str(summary['TOTAL'])   + ')'
    else:
        return 'Unknown'
    
    return summary