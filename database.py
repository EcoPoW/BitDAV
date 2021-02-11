
import os
import sqlite3
import json
import uuid

conn = None
def get_conn(current_name = None):
    global conn
    if conn:
        return conn

    if not os.path.exists('%s.db' % current_name):
        conn = sqlite3.connect('%s.db' % current_name)
        c = conn.cursor()

        # Create table
        c.execute('''CREATE TABLE "chain" (
                "id"	INTEGER,
                "hash"	TEXT NOT NULL,
                "prev_hash"	TEXT NOT NULL,
                "height"	INTEGER NOT NULL,
                "timestamp"	INTEGER NOT NULL,
                "data"	TEXT NOT NULL,
                PRIMARY KEY("id" AUTOINCREMENT)
            )''')

        # Insert a row of data
        c.execute("INSERT INTO chain(hash, prev_hash, height, timestamp, data) VALUES (?, ?, 0, CURRENT_TIMESTAMP, '{}')", (uuid.uuid4().hex, uuid.uuid4().hex))

        # Save (commit) the changes
        conn.commit()

        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        # conn.close()

    else:
        conn = sqlite3.connect('%s.db' % current_name)
