from requests import Session
from urllib.parse import urlparse, uses_netloc
import os
import json
import psycopg2
import sys


def json_parse(response_text):
    obj = json.loads(response_text)
    return obj['response']

def get_user(user_id):
    session = Session()
    session.headers['Accept'] = 'application/json'
    session.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    response = session.post(
        url='http://api.vk.com/method/users.get',
        params={
            'user_ids': user_id,
            'fields': 'online,last_seen',
            'name_case': 'Nom',
            'v': '5.29',
        }
    )
    return json_parse(response.text)[0]

if __name__ == '__main__':
    user = get_user('zelark')
    user_id = user['id']
    online = user['online']
    last_seen = user['last_seen']['time']
    
    uses_netloc.append("postgres")
    url = urlparse(os.environ["DATABASE_URL"])

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
