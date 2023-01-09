from flask_restful import Resource
import json
import pandas as pd
import sqlite3

class FeedManager:
    def __init__(self, db_name):
        self.db = sqlite3.connect(db_name)
        self.current_id = 0
        self.check_current()

    def check_current(self):
        check = 0
        try:
            df = pd.read_sql('select * from meta_data where is_current = 1', self.db)
            check = df['fetch_id'].values[0]
        except pd.errors.DatabaseError as er:
            print(er)
        finally:
            self.current_id = check

    def send_all(self):
        if self.current_id:
            query = """
                select
                    tralbum_id, title, artist, published,
                    is_preorder, genres, band_name, label_origin,
                    price, currency, tralbum_url, spotify, image
                from "%s" """ % self.current_id
            df = pd.read_sql(query, self.db)
            return json.loads(df.to_json(orient='records')), 200
        else:
            return {'message': 'Unable to load content.'}, 204

    def send_details(self, album_id):
        if self.current_id:
            query = """
                select tralbum_id, tracks_num, album_description
                from "%s"
                where tralbum_id=:album_id """ % self.current_id

            df = pd.read_sql(query, self.db, params={'album_id': album_id})
            return json.loads(df.to_json(orient='records')), 200
        else:
            return {'message': 'Unable to load content.'}, 204


class Feed(Resource):
    def get(self, album_id=False):
        f = FeedManager('server_data.db')
        return f.send_details(album_id) if album_id else f.send_all()
