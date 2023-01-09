from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api
from uuid import uuid4

from .resources.feedlib import Feed
from .resources.filelib import Files
from .resources.searchlib import Search
from .resources.spotifylib import Spotify

app = Flask(__name__)
app.secret_key = str(uuid4())
CORS(app)
api = Api(app)


class Home(Resource):
    def get(self):
        return {'name': 'kendama-open', 'server_status': 'guitar'}, 200


api.add_resource(Home, '/')
api.add_resource(Feed, '/feed', '/feed/<int:album_id>', methods=['GET'])
api.add_resource(Search, '/search', methods=['POST'])
api.add_resource(Spotify, '/spotify', methods=['GET', 'POST', 'DELETE'])
api.add_resource(Files, '/files', '/files/<string:session_id>', methods=['GET', 'DELETE', 'PUT'])

if __name__ == '__main__':
    app.run(debug=True)
