from requests import Session
from urllib.parse import urlparse, uses_netloc
from datetime import datetime
import os
import json
import psycopg2
import sys


CHECKPOINT = 2


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

def json_parse(response_text):
    obj = json.loads(response_text)
    return obj['response']

def update_activity():

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
        cursor.execute("select user_id from vk_users")
        user_ids = [str(user_id[0]) for user_id in cursor.fetchall()]
        users = get_users(user_ids)
        current_minute = get_minute()

        for user in users:
            last_seen_ut = user['last_seen']['time']
            user_id = user['id']

            if is_last_seen_today(last_seen_ut):
                last_seen_minute = get_minute(last_seen_ut)
                state = '{{"{}":{}, "{}":{}}}'.format(
                    current_minute, user['online'],
                    last_seen_minute, CHECKPOINT
                )
            else:
                state = '{{"{}":{}}}'.format(current_minute, user['online'])

            cursor.execute("select update_activity(%s, %s::json)",
                (user_id, state))

        db_connection.commit()

    except psycopg2.DatabaseError as e:
        print('Error {}'.format(e))
        sys.exit(1)

    finally:
        if db_connection:
            db_connection.close()

def get_minute(unixtime=None):
    if not unixtime:
        dt = datetime.now()
    else:
        dt = datetime.fromtimestamp(unixtime)
    return dt.hour * 60 + dt.minute

def is_last_seen_today(last_seen_ut):
    today = datetime.now()
    last_seen = datetime.fromtimestamp(last_seen_ut)
    return today.day == last_seen.day


if __name__ == '__main__':
    update_activity()
