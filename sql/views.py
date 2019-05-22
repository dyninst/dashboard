def get_runs(db_conn, limit=None, order_by=None, runid=None):
    query = """
        select
            id,
            arch,
            vendor,
            os,
            kernel,
            kernel_version,
            libc,
            hostname,
            build_status,
            datetime(run_date) as date,
            datetime(upload_date) as upload_date,
            dyninst_commit,
            dyninst_branch,
            testsuite_commit,
            testsuite_branch,
            upload_file
        from run
        where 1=1 """
    
    if runid is not None:
        query += " and id = ? "
    if order_by is not None:
        query += " order by {0:s} desc".format(order_by)    
    if limit is not None:
        query += " limit {0:d}".format(int(limit))

    params = [runid]
    cur = db_conn.cursor()
    cur.execute(query, [p for p in params if p is not None])
    res = cur.fetchall()
    cur.close()
    return res

def get_most_recent_run(db_conn, new_runid, hostname=None):
    query = """
        select
            old_run.id,
            old_run.arch,
            old_run.vendor,
            old_run.os,
            old_run.kernel,
            old_run.kernel_version,
            old_run.libc,
            old_run.hostname,
            old_run.build_status,
            datetime(old_run.run_date) as date,
            datetime(old_run.upload_date) as upload_date,
            old_run.dyninst_commit,
            old_run.dyninst_branch,
            old_run.testsuite_commit,
            old_run.testsuite_branch,
            old_run.upload_file
        from
            run as cur_run,
            run as old_run
        where
            cur_run.id = ?
            and old_run.run_date < cur_run.run_date
        """
    
    if hostname is not None:
        query += """
            and cur_run.hostname = ?
            and cur_run.hostname = old_run.hostname
        """

    query += """
        order by
            old_run.run_date desc,
            old_run.upload_date desc
        limit 1
    """
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
