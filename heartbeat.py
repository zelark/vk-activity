from requests import Session
from urllib.parse import urlparse
import os
import json
import time
import psycopg2
import sys


def unix2human(unixtime):
    return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(unixtime))

def json_parse(response_text):
    decoder = json.JSONDecoder(strict=False)
    idx = 0
    obj, idx = decoder.raw_decode(response_text, idx)
    return obj['response']

def users_get(user_ids):
    session = Session()
    session.headers['Accept'] = 'application/json'
    session.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    response = session.post(
        url='http://api.vk.com/method/users.get',
        params={
            'user_ids': user_ids,
            'fields': 'online,last_seen',
            'name_case': 'Nom',
            'v': '5.29',
        }
    )
    return json_parse(response.text)

if __name__ == '__main__':
    
    teamuse = users_get('teamuse')[0]
    user_id = teamuse['id']
    online = teamuse['online']
    last_seen = teamuse['last_seen']['time']
    
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])

    db_connection = None
    try:
        db_connection = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = db_connection.cursor()
        cursor.execute(
            "insert into heartbeat " \
            "(user_id, online, last_seen, log_time) " \
            "values (%s, %s, to_timestamp(%s), 'now');",
            (user_id, online, last_seen))
        db_connection.commit()
    
    except psycopg2.DatabaseError as e:
        print('Error %s' % e)
        sys.exit(1)

    finally:
        if db_connection:
            db_connection.close()
