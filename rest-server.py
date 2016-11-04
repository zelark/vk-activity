from flask import Flask, request, _app_ctx_stack 
from flask import render_template, url_for
from flask_restful import Api, Resource, reqparse, inputs
from flask_restful import reqparse
from urllib.parse import urlparse, uses_netloc
from apscheduler.schedulers.background import BackgroundScheduler
from vk_activity import update_activity 
import os, sys
import psycopg2


app = Flask(__name__)
app.config.from_object(__name__)
api = Api(app)


uses_netloc.append("postgres")
db_url = urlparse(os.environ["DATABASE_URL"])


scheduler = BackgroundScheduler()
scheduler.add_job(update_activity, 'interval', seconds=60)
scheduler.start()
print('scheduler is running...')


def get_db():
    """Opens a new database connection if there is none yet for
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'pg_db'):
        top.pg_db = psycopg2.connect(
            database=db_url.path[1:],
            user=db_url.username,
            password=db_url.password,
            host=db_url.hostname,
            port=db_url.port
        )
    return top.pg_db


@app.teardown_appcontext
def close_connection(exception):
    """Closes the datbase connection again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'pg_db'):
        top.pg_db.close()


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('init_db.sql', mode='r') as f:
        db.cursor().execute(
            f.read().replace('{{user-role}}', db_url.username)
        )
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Updates the database scheme."""
    init_db()
    print('Initialized the database.')


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

    def get(self, user_id):
        args = self.reqparse.parse_args()
        date = args['date']
        if date:
            date = date.strftime('%Y%m%d')
        response = None
        db = get_db()
        try:
            cursor = db.cursor()
            if not date:
                cursor.execute("select current_state(%s)", (user_id,))
            else:
                cursor.execute(
                    "select current_state(%s, %s::date)",
                    (user_id, date)
                )
            response = cursor.fetchone()[0]
            db.commit()
        except psycopg2.DatabaseError as e:
            print('Error: {}'.format(e))
            sys.exit(1)
        if response:
            return response, 200
        else:
            return {'error': 'Not found'}, 404


api.add_resource(UserAPI,
                 '/vk/activity/v1.0/users/id<int:user_id>',
                 '/vk/activity/v1.0/users/<user_id>',
                 endpoint='user')
