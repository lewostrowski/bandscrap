import json
import pandas as pd
import sqlite3


class FileManager:
    def __init__(self, db_name):
        self.db = sqlite3.connect(db_name)

    def print_files(self):
        df = pd.DataFrame()
        try:
            df = pd.read_sql_query('meta_data', self.db)
        except pd.errors.DatabaseError as er:
            print(er)
        finally:
            if not df.empty:
                return json.loads(df.to_json(orient='records')), 200
            else:
                return {'message': 'No files to load.'}, 204

    def save_file(self, session_id):
        save_query = 'UPDATE meta_data set is_saved=1 where is_saved=0 and fetch_id=:fetch'
        pd.read_sql_query(save_query, self.db, params={'fetch': session_id})
        return {'message': 'File deleted.'}, 200

    def load_file(self, session_id):
        # Clear current.
        pd.read_sql('UPDATE meta_data set is_current=0 where is_current=1', self.db)

        # Drop unsaved.
        to_remove = pd.read_sql_query('select fetch_id from meta_data where is_current=0 and is_saved=0', self.db)
        for t in to_remove['fetch_id']:
            pd.read_sql('delete from meta_data where fetch_id="%s"' % t, self.db)
            pd.read_sql('drop table "%s"' % t, self.db)

        # Change selected session as current.
        pd.read_sql('UPDATE meta_data set is_current=1 where is_current=0 and fetch_id=:session',
                    self.db, params={'session': session_id})

        self.db.commit()
        return {'message': 'File loaded.'}, 200

    def delete_file(self, session_id):
        pd.read_sql('delete from meta_data where fetch_id=:session', self.db, params={'session': session_id})
        pd.read_sql('drop table :session', self.db, params={'session': session_id})

        self.db.commit()
        return {'message': 'File deleted.'}, 200

