from requests import Session
from urllib.parse import urlparse, uses_netloc
from datetime import datetime
import os
import json
import psycopg2
import sys


def current_minute():
    dt = datetime.now()
    return dt.hour * 60 + dt.minute

def json_parse(response_text):
    obj = json.loads(response_text)
    return obj['response']

def get_users(user_ids):
    session = Session()
    session.headers['Accept'] = 'application/json'
    session.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    response = session.post(
        url='http://api.vk.com/method/users.get',
        params={
            'user_ids': ','.join(user_ids),
            'fields': 'online,last_seen',
            'name_case': 'Nom',
            'v': '5.29',
        }
    )
    return json_parse(response.text)

def update_activity():
    user = get_users(['zelark'])[0]
    user_id = user['id']
    state = '{{"{}":{}}}'.format(current_minute(), user['online'])
    
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
        cursor.execute("select update_activity(%s, %s::json)", (user_id, state))
        db_connection.commit()
    
    except psycopg2.DatabaseError as e:
        print('Error {}'.foramt(e))
        sys.exit(1)

    finally:
        if db_connection:
            db_connection.close()
