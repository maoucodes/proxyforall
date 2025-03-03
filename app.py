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

    if not url:
        return jsonify({'error': 'Missing URL parameter'}), 400

    try:
        res = requests.get(url, impersonate='chrome110')

        if type == 'text':
            return res.text

        elif type == 'json':
            return jsonify(res.json())  # Ensure valid JSON response

        else:
            return jsonify({'error': 'Invalid type parameter'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
