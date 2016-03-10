from requests import Session
from datetime import datetime
import os
import json
import psycopg2
import sys


def update_activity():
    db_url = os.environ["DATABASE_URL"]
    db = psycopg2.connect(db_url)

    with db:
        with db.cursor() as cursor:
            cursor.execute("select user_id from vk_users")
            user_ids = [str(user_id[0]) for user_id in cursor.fetchall()]
    users = get_vk_users(user_ids)
    current_minute = get_current_minute()

    for user in users:
        user_id = user['id']
        state = '{{"{}":{}}}'.format(current_minute, user['online'])
        print(user_id, state) 
        with db:
            with db.cursor() as cursor:
                cursor.execute("select update_activity(%s, %s::json)", (user_id, state))
        
    if db:
        db.close()

def get_vk_users(user_ids):
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

def get_current_minute():
    dt = datetime.now()
    return dt.hour * 60 + dt.minute


if __name__ == '__main__':
    update_activity()
