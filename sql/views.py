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
            new.test,
            new.comp,
            new.opt,
            new.abi,
            new.mode,
            new.thread,
            new.link,
            new.pic,
            old.result as previous_result,
            new.result as current_result
        from
            test_result as new
            join test_result as old on
                new.test = old.test
                and new.comp = old.comp
                and new.opt = old.opt
                and new.abi = old.abi
                and new.mode = old.mode
                and new.thread = old.thread
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
