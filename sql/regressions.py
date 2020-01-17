def create(db, cur_run, prev_run, cnt):
    query = """
        insert into regression_count(cur_run,prev_run,cnt) values(?,?,?)
    """
    cur = db.cursor()
    cur.execute(query, [str(cur_run), str(prev_run), str(cnt)])
    cur.close()

def counts(db, runid):
    query = """
        select
            sum(cnt)
        from
            regression_count
        where
            cur_run = ?
    """

    cur = db.cursor()
    cur.execute(query, [str(runid)])
    res = cur.fetchone()
    cur.close()
    return res[0] if res[0] else 0

def get(db_conn, cur_runid, prev_runid):
    """
        Find regressions between the run specified by `cur_runid`
        and the previous run specified by `prev_runid`

        NB: Regressions are not necessarily a reflexive relation
    """
    query = """
        select
            cur.test_name,
            cur.compiler,
            cur.optimization,
            cur.abi,
            cur.mode,
            cur.threading,
            cur.link,
            cur.pic,
            prev.result as previous_result,
            cur.result as current_result,
            cur.reason
        from
            test_result as cur
            join test_result as prev on
                cur.runid = ?
                and prev.runid = ?
                and cur.result in('CRASHED','FAILED')
                and prev.result not in('CRASHED','FAILED')
                and cur.result <> prev.result
                and cur.test_name = prev.test_name
                and cur.compiler = prev.compiler
                and cur.optimization = prev.optimization
                and cur.abi = prev.abi
                and cur.mode = prev.mode
                and cur.threading = prev.threading
                and cur.link = prev.link
                and cur.pic = prev.pic
    """
    cur = db_conn.cursor()
    cur.execute(query, [str(cur_runid), str(prev_runid)])
    res = cur.fetchall()
    cur.close()
    return res
