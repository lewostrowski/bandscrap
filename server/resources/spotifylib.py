from datetime import datetime
from flask import request
from flask_restful import Resource
import pandas as pd
import sqlite3


class SpotifyManager:
    def __init__(self, db_name):
        self.db = sqlite3.connect(db_name)
        self.cursor = self.db.cursor()

    def save_credentials(self):
        credentials = request.get_json()
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pd.DataFrame({
            'client_id': [credentials['client_id']],
            'client_secret': [credentials['client_secret']],
            'time': [time]
        }).to_sql('spotify_credentials', self.db, if_exists='replace', index=False)
        return {'message': 'Credentials saved.'}, 200

    def info_credentials(self):
        df = pd.DataFrame()
        try:
            df = pd.read_sql('select * from spotify_credentials', self.db)
        except pd.errors.DatabaseError as er:
            print(er)
        finally:
            if not df.empty:
                t = str(df['time'].values[0])
                return {'message': 'Spotify credentials presents.', 'up_time': t}, 200
            else:
                return {'message': 'No Spotify credentials.'}, 204

    def delete_credentials(self):
        success = 0
        try:
            self.cursor.execute('drop table spotify_credentials')
            self.db.commit()
            success = 1
        except Exception as er:
            print(er)
        finally:
            if success:
                return {'message': 'Credentials removed.'}, 200
            else:
                return {'message': 'No Spotify credentials.'}, 204


class Spotify(Resource):
    def get(self):
        s = SpotifyManager('server_data.db')
        return s.info_credentials()

    def post(self):
        s = SpotifyManager('server_data.db')
        return s.save_credentials()

    def delete(self):
        s = SpotifyManager('server_data.db')
        return s.delete_credentials()
