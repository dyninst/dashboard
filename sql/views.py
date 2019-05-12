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