def get_runs(db_conn, limit=None, order_by=None):
    query = """
        select
            id,
            arch,
            libc,
            hostname,
            build_status,
            date,
            dyninst_commit,
            dyninst_branch,
            testsuite_commit,
            testsuite_branch
        from run """
    
    if order_by is not None:
        query += " order by {0:s} desc".format(order_by)    
    if limit is not None:
        query += " limit {0:d}".format(int(limit))
    
    query = query.format()
    cur = db_conn.cursor()
    cur.execute(query)
    res = cur.fetchall()
    cur.close()
    return res

def get_most_recent_run(db_conn, new_runid, hostname=None):
    query = """
        select
            max(id)
        from
            run
        where
            id < ?
        """
    
    if hostname is not None:
        query += " and hostname = ?"
    
    cur = db_conn.cursor()
    params = [new_runid, hostname]
    cur.execute(query, [p for p in params if p is not None])
    res = cur.fetchall()
    cur.close()
    return res
    
def results_summary(db_conn, runid):
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

def regressions(db_conn, new_runid, old_runid):
    query = """
        select
            new.test_name,
            new.compiler,
            new.optimization,
            new.abi,
            new.mode,
            new.threading,
            new.link,
            new.pic,
            old.result as previous_result,
            new.result as current_result
        from
            test_result as new
            join test_result as old on
                new.test_name = old.test_name
                and new.compiler = old.compiler
                and new.optimization = old.optimization
                and new.abi = old.abi
                and new.mode = old.mode
                and new.threading = old.threading
                and new.link = old.link
                and new.pic = old.pic
        where
            new.runid = ?
            and old.runid = ?
            and new.result in('CRASHED','FAILED')
            and new.result <> old.result
    """
    cur = db_conn.cursor()
    cur.execute(query, [str(new_runid), str(old_runid)])
    res = cur.fetchall()
    cur.close()
    return res
