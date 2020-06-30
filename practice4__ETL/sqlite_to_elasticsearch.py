import sqlite3
import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


def extract():
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    movies_query = """
    SELECT m.id, m.genre, m.title, m.director, m.plot as description, m.imdb_rating, m.writer, m.writers, GROUP_CONCAT(ma.actor_id) as actors_id 
    FROM movies m 
    JOIN movie_actors ma ON ma.movie_id=m.id
    GROUP BY m.id
    """
    actors_query = "SELECT * from actors"
    writers_query = "SELECT * from writers"

    # get all movies with joined actors id
    cursor.execute(movies_query)
    movies = [dict(row) for row in cursor.fetchall()]

    # get all actors with names
    cursor.execute(actors_query)
    actors = [dict(row) for row in cursor.fetchall()]

    # get all writers with names
    cursor.execute(writers_query)
    writers = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {'movies': movies, 'actors': actors, 'writers': writers}


def transform(raw_data):
    movies = raw_data['movies']
    actors = raw_data['actors']
    writers = raw_data['writers']

    # list of docs for es bulk helper
    document_list = []

    for row in movies:
        doc = {
            "_index": "movies",
            "_id": row['id'],
            "id": row['id'],
            "imdb_rating": None if row['imdb_rating'] == 'N/A' else row['imdb_rating'],
            "genre": row["genre"],
            "title": row["title"],
            "description": row["description"],
            "director": row["director"],
            "actors": [],
            "writers": [],
            "actors_names": '',
            "writers_names": '',

        }

        # add nested writers to doc
        writers_id = []
        if row.get('writers'):
            writers_id = [item['id'] for item in json.loads(row['writers'])]
        if row.get('writer'):
            writers_id = row['writer']
        doc['writers'] = [{'id': item['id'], 'name': item['name']} for item in writers if str(item['id']) in writers_id]

        # replace all 'N/A' with None for correct load to elasticesearch
        for writer in doc['writers']:
            if writer['name'] == 'N/A':
                writer['name'] = None

        # helper field with only names of writers
        doc['writers_names'] = (', ').join([item['name'] for item in doc['writers'] if item['name']])

        # add nested actors to doc
        actors_id = [x.strip() for x in row['actors_id'].split(',')]
        doc['actors'] = [{'id': item['id'], 'name': item['name']} for item in actors if str(item['id']) in actors_id]

        # replace all 'N/A' with None for correct load to elasticsearch
        for actor in doc['actors']:
            if actor['name'] == 'N/A':
                actor['name'] = None

        # helper field with only names of actors
        doc['actors_names'] = (', ').join([item['name'] for item in doc['actors'] if item['name']])

        document_list.append(doc)

    return document_list


def load(actions_data):
    es = Elasticsearch(hosts='localhost:9200')
    result = bulk(es, actions_data)
    return result

if __name__ == "__main__":
    load(transform(extract()))
