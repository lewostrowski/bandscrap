from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api
from uuid import uuid4

from .resources.send_feed import FeedManager
from .resources.files_operation import FileManager

app = Flask(__name__)
app.secret_key = str(uuid4())
CORS(app)
api = Api(app)

db_name = 'server_data.db'


class Home(Resource):
    def get(self):
        return {'name': 'kendama-open', 'server_status': 'guitar'}


class Feed(Resource):
    def get(self, album_id=False):
        f = FeedManager(db_name)
        return f.send_details(album_id) if album_id else f.send_all()


class Files(Resource):
    def get(self, session_id=0):
        f = FileManager(db_name)
        return f.load_file(session_id) if session_id else f.print_files()

    def put(self, session_id):
        f = FileManager(db_name)
        return f.save_file(session_id)

    def delete(self, session_id):
        f = FileManager(db_name)
        return f.delete_file(session_id)


api.add_resource(Home, '/')
api.add_resource(Feed, '/feed', '/feed/<int:album_id>', methods=['GET'])
api.add_resource(Files, '/files', '/files/<string:session_id>', methods=['GET', 'DELETE', 'PUT'])

if __name__ == '__main__':
    app.run(debug=True)
