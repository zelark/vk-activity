from flask import Flask
from flask.ext.restful import Api, Resource
from flask.ext.restful import reqparse
from urllib.parse import urlparse, uses_netloc
import os
import psycopg2


app = Flask(__name__, static_url_path='')
api = Api(app)

@app.route('/')
def root():
    return app.send_static_file('heartbeat.html')

class UserAPI(Resource):
    def get(self, id):

        uses_netloc.append("postgres")
        url = urlparse(os.environ["DATABASE_URL"])

        # todo: make jsonify response
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
            cursor.execute("select current_state(%s)", (id,))
            response = cursor.fetchone()[0]
            db_connection.commit()
        except psycopg2.DatabaseError as e:
            print('Error %s' % e)
            sys.exit(1)
        finally:
            if db_connection:
                db_connection.close()

        return response, 200

api.add_resource(UserAPI, '/vk/activity/v1.0/users/<int:id>', endpoint='user')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
