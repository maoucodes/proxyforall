from flask import Flask, request, jsonify
from flask_cors import CORS
from curl_cffi import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return jsonify({'message': 'Hello, Proxy Server Running Successfully!'})

@app.route('/proxy/<type>')
def proxy_type(type):
    url = request.args.get('url')

    if type == 'text':
        res = request.get(url=url, impersonate='chrome110')
        return res.text

    elif type == 'json':
        res = request.get(url=url, impersonate='chrome110')
        return res.json()

    else:
        return jsonify({'message': 'Hello, Soemthing went wrong'})
