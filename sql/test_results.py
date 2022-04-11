def counts(db_conn, runid):
    query = """
        select
            passed,
            failed,
            skipped,
            crashed,
            hanged
        from
            test_result_summary
        where
            runid = ?
        """
    cur = db_conn.cursor()
    cur.execute(query, [str(runid)])
    res = cur.fetchall()
    cur.close()
    return res

def bulk_insert(db_conn, runid, logfile):
    fields = [
        'runid', 'test_name',
        'compiler', 'optimization',
        'abi', 'mode', 'threading',
        'link', 'pic', 'result', 'reason'
    ]
    
    counts = {
        'PASSED':0,
        'FAILED':0,
        'SKIPPED':0,
        'CRASHED':0,
        'HANGED':0
    }

    db_conn.execute('BEGIN TRANSACTION')
    for result in logfile:
        values = [runid]
        values.extend(result)
        if len(values) > 1:
            query = "INSERT INTO test_result({0:s}) VALUES ({1:s})".format(','.join(fields),','.join(['?']*len(values)))
            db_conn.execute(query, values)
            counts[values[-2]] += 1

    query = "INSERT INTO test_result_summary(runid,passed,failed,skipped,crashed,hanged) VALUES (?,?,?,?,?,?)"
    db_conn.execute(query, [runid, counts['PASSED'], counts['FAILED'], counts['SKIPPED'], counts['CRASHED'], counts['HANGED']])
    
    db_conn.commit()

def get(db, runid, result=None):
    query = """
        select
            *
        from test_result
        where
            runid=?          
    """
    
    params = [str(runid)]
    if result is not None:
        query += " and result = ? "
        params.append(str(result))

    cur = db.cursor()
    cur.execute(query, params)
    res = cur.fetchall()
    cur.close()
    return res
