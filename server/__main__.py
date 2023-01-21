from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from uuid import uuid4

from .resources.feedlib import Feed
from .resources.filelib import Files
from .resources.searchlib import Search
from .resources.spotifylib import Spotify
from .resources.userslib import Users

app = Flask(__name__)
app.secret_key = str(uuid4())
CORS(app)
api = Api(app)

api.add_resource(Users, '/', '/<str:user>', methods=['GET', 'DELETE'])
api.add_resource(Feed, '/<str:user>/feed', '/<str:user>/feed/<int:album_id>', methods=['GET'])
api.add_resource(Search, '/<str:user>/search', methods=['POST'])
api.add_resource(Spotify, '/<str:user>/spotify', methods=['GET', 'POST', 'DELETE'])
api.add_resource(Files, '/<str:user>/files', '/<str:user>/files/<string:session_id>', methods=['GET', 'DELETE', 'PUT'])

if __name__ == '__main__':
    app.run(debug=True)
