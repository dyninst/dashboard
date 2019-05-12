import sqlite3
import csv

def _insert_single(table, fields, values):
    """ Not for external consumption """
    if len(fields) != len(values):
        raise "Invalid insert into {0:s}\n {1:s}\n {2:s}\n".format(table,','.join(fields),','.join(values))

    query = "INSERT INTO {0:s}({1:s}) VALUES ({2:s})".format(table,','.join(fields),','.join(['?']*len(values)))
    db = sqlite3.connect("test.sqlite3")
    cur = db.cursor()
    cur.execute(query, values)
    db.commit()
    rowid = cur.lastrowid
    cur.close()
    return rowid

def create_run(properties):
    fields = [
        'arch', 'os', 'kernel',
        'libc', 'hostname', 'build_status',
        'dyninst_commit', 'dyninst_branch',
        'testsuite_commit', 'testsuite_branch'
    ]
    values = [properties[k] for k in fields]
    
    # Manually set the creation datetime
    fields.append('date')
    values.append("datetime('now')")
    
    fields.append('kernel_version')
    values.append(properties['version'])
    
    fields.append('upload_file')
    values.append(properties['user_file'])

    return _insert_single('run', fields, values)