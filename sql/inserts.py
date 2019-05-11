import sqlite3

def insert_single(table, fields, values):
    if len(fields) != len(values):
        raise "Invalid insert into {0:s}\n {1:s}\n {2:s}\n".format(table,','.join(fields),','.join(values))

    query = 'INSERT INTO {0:s}({1:s}) VALUES ({2:s})'.format(table,fields,'?'*len(values))
    db = sqlite3.connect("test.sqlite3")
    cur = db.cursor()
    cur.execute(query, '')
    db.commit()
    rowid = cur.lastrowid
    cur.close()
    return rowid
