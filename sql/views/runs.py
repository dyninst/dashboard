def runs(db_conn, limit=None, order_by=None, runid=None):
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
            tests_status,
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

def _create_most_recent_table(db, runid):
    """
        !!! Internal use only !!!
        
        Select the most recent run on every host,
        except the one specified by 'runid',
        with the same architecture as the run
        the one specified by 'runid'
    """
    query = """
        create temporary table most_recent as
        select
            run.id id
        from
            run
            join run as excluded_run on
                excluded_run.id = ?
        where
            run.tests_status <> 'FAILED'
            and run.build_status <> 'FAILED'
            and run.id <> excluded_run.id
            and run.arch = excluded_run.arch
            and run.run_date < excluded_run.run_date
        group by
            run.arch,
            run.hostname
        having
            run.run_date = max(run.run_date);
    """

    cur = db.cursor()
    cur.execute("drop table if exists most_recent;")
    cur.execute(query, [str(runid)])
    cur.close()

def most_recent_runs_by_arch(db, exclude_run):
    query = """
        select
            run.id,
            run.arch,
            run.vendor,
            run.os,
            run.kernel,
            run.kernel_version,
            run.libc,
            run.hostname,
            run.build_status,
            run.tests_status,
            datetime(run.run_date) as date,
            datetime(run.upload_date) as upload_date,
            run.dyninst_commit,
            run.dyninst_branch,
            run.testsuite_commit,
            run.testsuite_branch,
            run.upload_file
        from
            run
            join run as excluded_run on
                excluded_run.id = ?
        where
            run.tests_status <> 'FAILED'
            and run.build_status <> 'FAILED'
            and run.id <> excluded_run.id
            and run.arch = excluded_run.arch
        group by
            run.hostname
        having
            run.run_date = max(run.run_date);
        """
    
    cur = db.cursor()
    cur.execute(query, [str(exclude_run)])
    res = cur.fetchall()
    cur.close()
    return res
