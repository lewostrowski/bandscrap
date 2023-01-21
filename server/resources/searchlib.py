from bs4 import BeautifulSoup
from datetime import datetime
from flask import request
from flask_restful import Resource
import json
import pandas as pd
import requests
import sqlite3
from uuid import uuid4

from server.common.genres import GenresSmasher


class SearchEngine:
    def __init__(self, search_query, user):
        self.search_query = search_query
        self.user = user
        self.fetch = []
        self.enriched = []
        self.spotify_enriched = []

    def bc_basic(self):
        fin_responses = []
        tags = [t.strip().lower().replace(' ', '-') for t in self.search_query['tags'].split(',')]
        for i in range(1, self.search_query['depth'] + 1):
            response = 0
            api_link = 'https://bandcamp.com/api/hub/2/dig_deeper'
            # body: '{"sort": "date", "type_": "all", depth: 1, "tags": "ambient, drone"}'
            filter_dict = {"filters":
                               {"sort": self.search_query['sort'],
                                "format": self.search_query['type_'],
                                "tags": tags,
                                "location": 0},
                           "page": i}

            try:
                response = requests.post(api_link, data=json.dumps(filter_dict))
                time = datetime.now().strftime('%H:%M:%S')
                print('{} Fetching page: {}/{}'.format(time, str(i), str(self.search_query['depth'])))
            except requests.exceptions.ConnectionError as e:
                print(e)
            finally:
                if response:
                    for album in json.loads(response.text)['items']:
                        # artist = artist, band_name = label
                        search = ['title', 'artist', 'band_name', 'is_preorder', 'tralbum_url', 'tralbum_id']
                        album_dict = {attr: album[attr] for attr in search}
                        self.fetch.append(album_dict)
                    fin_responses.append(1)
                else:
                    fin_responses.append(0)

        if 0 in fin_responses:
            return 0
        else:
            return 1

    def bc_advance(self):
        fin_responses = []
        for album in self.fetch:
            response = 0

            try:
                response = requests.get(album['tralbum_url'])
                time = datetime.now().strftime('%H:%M:%S')
                print('{} Fetching album: {}/{}'.format(time, len(self.enriched) + 1, len(self.fetch)))
            except requests.exceptions.ConnectionError as e:
                print(e)
            finally:
                if response:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    info = json.loads(soup.find('script').text)
                    album_enrichment = {
                        'price': info['albumRelease'][0].get('offers').get('price'),
                        'currency': info['albumRelease'][0].get('offers').get('priceCurrency'),
                        'tracks_num': info['numTracks'],
                        'published': datetime.strptime(info['datePublished'], '%d %b %Y %H:%M:%S %Z').strftime(
                            '%Y-%m-%d'),
                        'genres': [k.lower() for k in info['keywords']],
                        'image': info['albumRelease'][0]['image'][0],
                        'spotify': None,
                        'dsc': info['description'] if 'description' in info.keys() else None,
                        'label_origin': info['publisher']['foundingLocation']['name'] if 'foundingLocation' in info[
                            'publisher'].keys() else None
                    }
                    album.update(album_enrichment)
                    self.enriched.append(album)
                    fin_responses.append(1)
                else:
                    fin_responses.append(0)

        if 0 in fin_responses:
            return 0
        else:
            return 1

    def spotify(self, credentials):
        header = 0

        try:
            auth_response = requests.post('https://accounts.spotify.com/api/token', data={
                'grant_type': 'client_credentials',
                'client_id': credentials[0],
                'client_secret': credentials[1]
            })

            time = datetime.now().strftime('%H:%M:%S')
            if auth_response.status_code == 200:
                header = {'Authorization': 'Bearer {}'.format(auth_response.json().get('access_token'))}
                print(f'{time} Spotify authorization token received')
            else:
                print(f'{time} Wrong Spotify credentials')

        except requests.exceptions.ConnectionError as e:
            print(e)
        finally:
            if header:
                for album in self.enriched:
                    artist = album['artist'].replace(' ', '%20').replace('+', '')
                    title = album['title'].replace(' ', '%20').replace('+', '')
                    year = album['published'][:4]
                    search_string = f'artist:{artist}+album:{title}+year:{year}'
                    search_full = f'https://api.spotify.com/v1/search?type=album&q={search_string}&limit=1'

                    spotify_response = 0
                    try:
                        spotify_response = requests.get(search_full, headers=header)
                        time = datetime.now().strftime('%H:%M:%S')
                        console = 'Fetching spotify info for album'
                        print('{} {} {}/{}'.format(time, console, len(self.spotify_enriched) + 1, len(self.enriched)))
                    except requests.exceptions.ConnectionError as e:
                        print(e)
                    finally:
                        if spotify_response:
                            spotify = json.loads(spotify_response.text)['albums']['items']
                            if spotify:
                                s_url = spotify[0]['external_urls']['spotify']
                                album.update({'spotify': s_url})

                        self.spotify_enriched.append(album)

                return 1
            else:
                return 0

    def create_meta(self):
        fetch_id = str(uuid4()).replace('-', '')
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        items_num = len(self.enriched)
        tags = [t.strip().lower().replace(' ', '-') for t in self.search_query['tags'].split(',')]
        return {
            'fetch_id': [fetch_id],
            'fetch_date': [time],
            'is_current': [True],
            'is_saved': [False],
            'items': [items_num],
            'genres': [','.join(tags)],
            'depth': [self.search_query['depth']],
            'sort': [self.search_query['sort']],
            'type': [self.search_query['type_']],
            'spotify_search': [self.search_query['spotify']],
            'user': [self.user]
        }

class Search(Resource):
    def post(self, user):
        search = request.get_json()
        engine = SearchEngine(search, user)
        basic = engine.bc_basic()

        if basic:
            advance = engine.bc_advance()
        else:
            return {'message': 'Basic fetch failed.'}, 500

        if advance:
            db = sqlite3.connect('server_data.db')
            table_list = pd.read_sql('select name from sqlite_master where type="table"', db)['name']
        else:
            return {'message': 'Advance fetch failed.'}, 500

        # Spotify.
        if search['spotify'] and 'spotify_credentials' in set(table_list):
            query = 'select * from spotify_credentials where user=:user'
            credentials = pd.read_sql(query, db, params={'user': user}).to_records(index=False)
            sptf = engine.spotify(credentials[0])
        else:
            sptf = 0

        meta = engine.create_meta()
        results = engine.spotify_enriched if sptf else engine.enriched

        # Delete unsaved.
        if 'meta_data' in set(table_list):
            cursor = db.cursor()

            cursor.execute('update meta_data set is_current=0 where is_current=1 and user=?', (user,))
            not_saved = pd.read_sql_query('select fetch_id from meta_data where is_current=0 and is_saved=0', db)
            for t in (not_saved['fetch_id']):
                cursor.execute('drop table "%s"' % t)
                cursor.execute('delete from meta_data where fetch_id="%s"' % t)

        new_fetch = pd.DataFrame(results)
        for c in new_fetch.columns:
            if new_fetch[c].dtypes == 'object':
                new_fetch[c] = new_fetch[c].astype('string')

        new_fetch = GenresSmasher(new_fetch).smash()
        new_fetch.to_sql(meta['fetch_id'][0], db, if_exists='replace', index=False)
        pd.DataFrame(meta).to_sql('meta_data', db, if_exists='append', index=False)
        db.commit()

        return {'message': 'Fetch success.'}, 200
