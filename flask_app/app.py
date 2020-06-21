from flask import Flask
from flask import request, make_response
app = Flask(__name__)

@app.route('/client/info', methods=['GET'])
def hello():
    user_agent = request.headers.environ['HTTP_USER_AGENT']
    resp = make_response(
        {
            'user_agent':user_agent
        }
    )
    resp.headers['Content-Type'] = 'application/json'
    return resp