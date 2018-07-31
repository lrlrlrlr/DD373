import sqlite3

conn=sqlite3.connect(('example.db'))
c=conn.cursor()
for row in c.execute("SELECT * FROM test;"):
    print(row)

conn.commit()
conn.close()