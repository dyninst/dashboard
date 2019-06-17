def summary(db_conn, runid):
    query = """
        select
            status.name as result,
            sum(case when test.result is null then 0 else 1 end) as cnt
        from status
        left outer join test_result as test on
            test.result = status.name
            and test.runid = ?
        group by status.name
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

    db_conn.execute('BEGIN TRANSACTION')
    for result in logfile:
        values = [runid]
        values.extend(result)
        if len(values) > 1:
            query = "INSERT INTO test_result({0:s}) VALUES ({1:s})".format(','.join(fields),','.join(['?']*len(values)))
            db_conn.execute(query, values)

    db_conn.commit()