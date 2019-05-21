def create_run(db_conn, properties):
    fields = [
        'arch', 'os', 'kernel',
        'libc', 'hostname', 'build_status',
        'dyninst_commit', 'dyninst_branch',
        'testsuite_commit', 'testsuite_branch'
    ]
    values = [properties[k] for k in fields]
    
    fields.append('kernel_version')
    values.append(properties['version'])
    
    fields.append('upload_file')
    values.append(properties['user_file'])
    
    fields.append('run_date')
    values.append(properties['date'])

    # datetime is UTC
    query = "INSERT INTO run({0:s},upload_date) VALUES ({1:s},datetime('now'))"
    query = query.format(','.join(fields),','.join(['?']*len(values)))
    cur = db_conn.cursor()
    cur.execute(query, values)
    db_conn.commit()
    rowid = cur.lastrowid
    cur.close()
    return rowid

def save_results(db_conn, runid, logfile):
    fields = [
        'runid', 'test_name',
        'compiler', 'optimization',
        'abi', 'mode', 'threading',
        'link', 'pic', 'result', 'reason'
    ]

    db_conn.execute('BEGIN TRANSACTION')
    for result in logfile:
        values = [runid]
        values.extend(result)
        if len(values) > 1:
            query = "INSERT INTO test_result({0:s}) VALUES ({1:s})".format(','.join(fields),','.join(['?']*len(values)))
            db_conn.execute(query, values)

    db_conn.commit()
