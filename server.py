import hashlib
import hmac
import json

from flask import request, jsonify
from authlib.integrations.flask_client import OAuth
from app import create_app
from flask_cors import CORS
from auth import AuthError
from routes import EventRoutes, UserRoutes, TrashRoutes

import os
from dotenv import load_dotenv

load_dotenv('.env')

app = create_app()
cors = CORS(app, resources={r"*": {"origins": "*"}})
oauth = OAuth(app)

app.register_blueprint(EventRoutes)
app.register_blueprint(UserRoutes)
app.register_blueprint(TrashRoutes)


@app.route('/shutdown', methods=['POST'])
def shutdown():
    if not request.json or 'ref' not in request.json:
        return jsonify({'success': False})
    if request.json['ref'] != 'refs/heads/master':
        return jsonify({'success': False})

    key = bytes(os.environ.get('SHUTDOWN_SECRET'), 'UTF-8')
    message = bytes(json.dumps(request.json, separators=(',', ':')), 'UTF-8')

    digest = hmac.new(key, message, hashlib.sha1)
    signature = digest.hexdigest()

    if signature != request.headers.get('x-hub-signature')[5:]:
        return jsonify({'success': False})

    shut_down = request.environ.get('werkzeug.server.shutdown')
    if shutdown is None:
        raise RuntimeError('Shutting down...')
    else:
        shut_down()


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
