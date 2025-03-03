from flask import Flask, request, jsonify
from flask_cors import CORS
from curl_cffi import requests
import logging
from functools import wraps
import time
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMIT = 100  # requests per minute
request_history = {}

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        current_time = time.time()
        
        # Clean up old entries
        request_history[ip] = [t for t in request_history.get(ip, []) 
                             if current_time - t < 60]
        
        if len(request_history.get(ip, [])) >= RATE_LIMIT:
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        request_history.setdefault(ip, []).append(current_time)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@rate_limit
def hello_world():
    return jsonify({'message': 'Hello, Proxy Server Running Successfully!'})

@app.route('/proxy/<method>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit
def proxy_route(method):
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({'error': 'URL parameter is required'}), 400

        # Get request headers and remove any sensitive ones
        headers = {k: v for k, v in request.headers.items()
                  if k.lower() not in ['host', 'authorization']}
        
        # Get request data for non-GET methods
        data = request.get_data() if request.method != 'GET' else None
        
        # Make the request
        response = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=data,
            impersonate='chrome110',
            timeout=30
        )

        if method == 'text':
            return response.text
        elif method == 'json':
            return response.json()
        elif method == 'raw':
            return response.content
        else:
            return jsonify({'error': 'Invalid method'}), 400

    except requests.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=False)
