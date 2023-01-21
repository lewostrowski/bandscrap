from flask_restful import Resource
import json
import pandas as pd
import sqlite3


class UsersManager:
    def __init__(self, db_name, user):
        self.db = sqlite3.connect(db_name)
        self.cursor = self.db.cursor()
        self.user = user

    def print_users(self):
        df = pd.DataFrame()
        try:
            df = pd.read_sql('select distinct user from meta_data', self.db)
        except pd.errors.DatabaseError as er:
            print(er)
        finally:
            if not df.empty:
                return json.loads(df.to_json(orient='records')), 200
            else:
                return {'message': 'No users detected.'}, 204

    def delete_user(self):
        df = pd.DataFrame()
        try:
            df = pd.read_sql('select fetch_id from meta_data where user=:user', self.db, params={'user': self.user})
        except pd.errors.DatabaseError as er:
            print(er)
        finally:
            if not df.empty:
                self.cursor.execute('delete from meta_data where user=?', (self.user,))
                for fetch_id in df['fetch_id']:
                    self.cursor.execute('drop table "%s"' % fetch_id)
                return {'message': 'User and user\'s files deleted.'}, 200
            else:
                return {'message': 'No user detected.'}, 204

class Users(Resource):
    # User is created after it's first search.
    def get(self):
        u = UsersManager('server_data.db', None)
        return u.print_users()

    def delete(self, user):
        u = UsersManager('server_data.db', user)
        return u.delete_user()