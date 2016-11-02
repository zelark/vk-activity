import os
import psycopg2
from urllib.parse import urlparse, uses_netloc


uses_netloc.append("postgres")
url = urlparse(os.environ["DATABASE_URL"])

sql = open('init_db.sql', 'r').read()
sql = sql.replace('{{user-role}}', url.username)

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

cursor = conn.cursor()
cursor.execute(sql)

conn.commit()

cursor.close()
conn.close()
