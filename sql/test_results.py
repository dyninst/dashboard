def status_names(db):
    cur = db.cursor()
    cur.execute("select name from status")
    res = cur.fetchall()
    cur.close()
    return res

def counts(db_conn, runid):
    query = """
        select
            result,
            count(1) as cnt
        from test_result
        where
            runid = ?
        group by result
        """
    cur = db_conn.cursor()
    cur.execute(query, [str(runid)])
    res = cur.fetchall()
    cur.close()
    return res

def insert_hangs(db, runid, test_names):
    db.execute('BEGIN TRANSACTION')
    
    for n in test_names:
        query = "INSERT INTO test_result('runid', 'test_name', 'result') VALUES (?,?,?)"
        db.execute(query, [runid, n, 'HANGED'])
    
    db.commit()

def bulk_insert(db_conn, runid, logfile):
    fields = [
        'runid', 'test_name',
        'compiler', 'optimization',
        'abi', 'mode', 'threading',
        'link', 'pic', 'result', 'reason'
    ]

    db_conn.execute('BEGIN TRANSACTION')
    for result in logfile:
        values = [runid]
        values.extend(result)
        if len(values) > 1:
            query = "INSERT INTO test_result({0:s}) VALUES ({1:s})".format(','.join(fields),','.join(['?']*len(values)))
            db_conn.execute(query, values)

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
