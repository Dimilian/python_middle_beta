import json
from urllib.parse import urljoin

from flask import Flask
from flask import request, make_response, jsonify

import requests

from practice5__API.validators import positive_int, sort_by, sort_order

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/api/movies', methods=['GET'])
def movies():
    DEFAULT_SIZE = 50
    DEFAULT_SORT_BY = 'id'
    DEFAULT_SORT = 'asc'
    DEFAULT_PAGE = 1

    params = {key: value.replace('"', '') for (key, value) in request.args.items()}

    # validation part
    validate_params = validate_movies_params(params)
    if not validate_params['valid']:
        return (jsonify(validate_params['errors']), 422)

    search_query = params.get('search')

    query = {}
    if search_query:
        # query to ES if search param is not empty
        query = {
            "multi_match": {
                "query": search_query,
                "fields": ["title", "description", "writers_names", "actors_names", "director"]
            }
        }
    else:
        # query to ES if search param is empty. Got all movies
        query = {
            "match_all": {}
        }

    payload = {
        "_source": ['id', 'title', 'imdb_rating'],
        "size": params.get('limit', DEFAULT_SIZE),
        "from": (int(params.get('page', DEFAULT_PAGE)) - 1) * int(params.get('limit', DEFAULT_SIZE)),
        "sort": {params.get('sort', DEFAULT_SORT_BY): {"order": params.get('sort_order', DEFAULT_SORT)}},
        "query": query
    }
    r = requests.get('http://localhost:9200/movies/_search', json=payload)
    result = json.loads(r.text)
    response = [m['_source'] for m in result['hits']['hits']]

    return jsonify(response), 200


@app.route('/api/movies/<movieID>', methods=['GET'])
@app.route('/api/movies/', methods=['GET'])
def movie(movieID=None):
    if not movieID:
        return (jsonify([]), 200)

    # query to ES
    query = {
        "term": {
            "_id": movieID
        }
    }

    payload = {
        "query": query
    }
    r = requests.get('http://localhost:9200/movies/_search', json=payload)
    es_movie_data = json.loads(r.text)
    if not es_movie_data['hits']['total']['value']:
        return 'movie not found', 404
    else:
        es_movie_data = es_movie_data['hits']['hits'][0]['_source']
        prepare_es_movie_data = {
            'id': es_movie_data['id'],
            'title': es_movie_data['title'],
            'description': es_movie_data['description'],
            'imdb_rating': float(es_movie_data['imdb_rating']),
            'writers': es_movie_data['writers'],
            'actors': es_movie_data['actors'],
            'genre': [genre.strip(' ') for genre in es_movie_data['genre'].split(',')],
            'director': [director.strip(' ') for director in es_movie_data['director'].split(',')],
        }
        return jsonify(prepare_es_movie_data), 200


def validate_movies_params(params):
    result = {
        'valid': True,
        'errors': []
    }

    if params.get('limit'):
        limit_validate_result = positive_int(params.get('limit'), 'limit')
        if not limit_validate_result['valid']:
            result['valid'] = False
            result['errors'].extend(limit_validate_result['errors'])

    if params.get('page'):
        page_validate_result = positive_int(params.get('page'), 'page')
        if not page_validate_result['valid']:
            result['valid'] = False
            result['errors'].extend(page_validate_result['errors'])

    if params.get('sort'):
        sort_validate_result = sort_by(params.get('sort'), ['id', 'title', 'imdb_rating'])
        if not sort_validate_result['valid']:
            result['valid'] = False
            result['errors'].extend(sort_validate_result['errors'])

    if params.get('sort_order'):
        sort_order_validate_result = sort_order(params.get('sort_order'))
        if not sort_order_validate_result['valid']:
            result['valid'] = False
            result['errors'].extend(sort_order_validate_result['errors'])

    return result


if __name__ == '__main__':
    app.run(debug=True, port=8000)
