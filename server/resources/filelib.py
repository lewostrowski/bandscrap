from flask_restful import Resource
import json
import pandas as pd
import sqlite3


class FileManager:
    def __init__(self, db_name):
        self.db = sqlite3.connect(db_name)
        self.cursor = self.db.cursor()

    def check_session(self, session_id):
        check = 0
        try:
            df = pd.read_sql('select fetch_id from meta_data where fetch_id=:session',
                             self.db,
                             params={'session': session_id})
            check = df['fetch_id'].values[0]
        except pd.errors.DatabaseError as er:
            print(er)
        finally:
            return check

    def print_files(self):
        df = pd.DataFrame()
        try:
            df = pd.read_sql('select * from meta_data', self.db)
        except pd.errors.DatabaseError as er:
            print(er)
        finally:
            if not df.empty:
                return json.loads(df.to_json(orient='records')), 200
            else:
                return {'message': 'No files to load.'}, 204

    def load_file(self, session_id):
        # Clear current.
        if self.check_session(session_id):
            self.cursor.execute('update meta_data set is_current=0 where is_current=1')

            # Drop unsaved.
            to_remove = pd.read_sql('select fetch_id from meta_data where is_current=0 and is_saved=0', self.db)
            for t in to_remove['fetch_id']:
                self.cursor.execute('delete from meta_data where fetch_id="%s"' % t)
                self.cursor.execute('drop table "%s"' % t)

            # Change selected session as current.
            self.cursor.execute('update meta_data set is_current=1 where is_current=0 and fetch_id=?', (session_id,))

            self.db.commit()
            return {'message': 'File loaded.'}, 200
        else:
            return {'message': 'Session does not exist.'}, 204

    def save_file(self, session_id):
        if self.check_session(session_id):
            self.cursor.execute('update meta_data set is_saved=1 where is_saved=0 and fetch_id=?', (session_id,))
            self.db.commit()
            return {'message': 'File saved.'}, 200
        else:
            return {'message': 'Session does not exist.'}, 204

    def delete_file(self, session_id):
        # If statement guarantee preservation of essentials tables.
        if self.check_session(session_id):
            self.cursor.execute('delete from meta_data where fetch_id=?', (session_id,))
            self.cursor.execute('drop table "%s"' % session_id)
            self.db.commit()
            return {'message': 'File deleted.'}, 200
        else:
            return {'message': 'Session does not exist.'}, 204


class Files(Resource):
    def get(self, session_id=0):
        f = FileManager('server_data.db')
        return f.load_file(session_id) if session_id else f.print_files()

    def put(self, session_id):
        f = FileManager('server_data.db')
        return f.save_file(session_id)

    def delete(self, session_id):
        f = FileManager('server_data.db')
        return f.delete_file(session_id)
