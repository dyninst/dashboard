def create(db, vendor, path, version, language):
    query = "INSERT INTO compiler(name,path,version,language) VALUES (?,?,?,?)"
    cur = db.cursor()
    cur.execute(query, [vendor, path, version, language])
    db.commit()
    rowid = cur.lastrowid
    cur.close()
    return rowid

def get(db, vendor, path, version, language):
    query = """
        select
            id
        from compiler
        where
            name = ?
            and path = ?
            and version = ?
            and language = ?
    """
    cur = db.cursor()
    cur.execute(query, [vendor, path, version, language])
    res = cur.fetchone()
    cur.close()

    if res:
        return res[0]
    return res

def by_run(db, runid):
    query = """
        select
            rc.target,
            name,
            path,
            version,
            language
        from
            compiler
            join run_compiler as rc on
                rc.compilerid = compiler.id
        where
            rc.runid = ?   
        order by
            rc.target,
            language
    """
    
    cur = db.cursor()
    cur.execute(query, [runid])
    res = cur.fetchall()
    cur.close()
    return res
