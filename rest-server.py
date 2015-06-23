from flask import Flask, request 
from flask import render_template, url_for
from flask.ext.restful import Api, Resource, reqparse, inputs
from flask.ext.restful import reqparse
from urllib.parse import urlparse, uses_netloc
from apscheduler.schedulers.background import BackgroundScheduler
from vk_activity import update_activity 
import os
import psycopg2


app = Flask(__name__)
api = Api(app)

scheduler = BackgroundScheduler()
scheduler.add_job(update_activity, 'interval', seconds=60)
scheduler.start()
print('scheduler is running...')

@app.route('/')
def index():
    return 'an example: http://hostname/[user_id]?date=YYYY-MM-DD'

@app.route('/<username>')
@app.route('/<int:username>')
def get_user_activity(username):
    return render_template('heartbeat.html')

class UserAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('date', type=inputs.date, location='values')

        super(UserAPI, self).__init__()

    def get(self, id):
        args = self.reqparse.parse_args()
        date = args['date']
        if date:
            date = date.strftime('%Y%m%d')

        uses_netloc.append("postgres")
        url = urlparse(os.environ["DATABASE_URL"])

        response = None
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
            if not date:
                cursor.execute("select current_state(%s)", (id,))
            else:
                cursor.execute("select current_state(%s, %s::date)", (id, date))
            response = cursor.fetchone()[0]
            db_connection.commit()

        except psycopg2.DatabaseError as e:
            print('Error: {}'.format(e))
            sys.exit(1)

        finally:
            if db_connection:
                db_connection.close()

        if response:
            return response, 200
        else:
            return {'error': 'Not found'}, 404

api.add_resource(UserAPI, '/vk/activity/v1.0/users/<int:id>', endpoint='user')
