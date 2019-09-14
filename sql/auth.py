def is_valid(db, token):
    query = """
        select
            count(1) as cnt
        from
            auth_token
        where
            token = ?
    """
    cur = db.cursor()
    cur.execute(query, [token])
    res = cur.fetchone()
    cur.close()
    return int(res['cnt']) == 1