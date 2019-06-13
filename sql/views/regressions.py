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
            new.result as current_result,
            new.reason
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