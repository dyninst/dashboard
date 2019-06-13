import sql.views.runs

def counts(db, runid):
    query = """
        select
            count(1) as cnt
        from
            test_result as cur
            join test_result as prev on
                cur.test_name = prev.test_name
                and cur.compiler = prev.compiler
                and cur.optimization = prev.optimization
                and cur.abi = prev.abi
                and cur.mode = prev.mode
                and cur.threading = prev.threading
                and cur.link = prev.link
                and cur.pic = prev.pic
            join most_recent on
                most_recent.id = prev.runid
            join run as prev_run on
                prev_run.id = prev.runid
            join run as cur_run on
                cur_run.id = cur.runid
        where
            cur.runid = ?
            and cur.result in('CRASHED','FAILED')
            and cur.result <> prev.result
            and prev_run.run_date < cur_run.run_date
    """
    
    sql.views.runs._create_most_recent_table(db, runid)
    
    cur = db.cursor()
    cur.execute(query, [str(runid)])
    res = cur.fetchone()
    cur.close()
    return res[0]

def by_arch(db_conn, cur_runid, prev_runid):
    """
        For the run given by `runid`, select all
        hosts of its same architecture against which
        its test results cause regressions
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
