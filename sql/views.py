import sqlite3

def results_summary(runid):
    db = sqlite3.connect("test.sqlite3")
    cur = db.cursor()
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
    cur.execute(query, str(runid))
    res = cur.fetchall()
    cur.close()
    return res

def regressions(new_runid, old_runid):
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
    
    db = sqlite3.connect("test.sqlite3")
    cur = db.cursor()
    cur.execute(query, str(new_runid), str(old_runid))
    res = cur.fetchall()
    cur.close()
    return res
