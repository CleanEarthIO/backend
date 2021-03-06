import hashlib
import hmac
import json

from flask import request, jsonify, send_file, send_from_directory
from app import create_app
from flask_cors import CORS
from auth import AuthError
from routes import EventRoutes, UserRoutes, TrashRoutes
from models import User
from subprocess import Popen
from flask_login import LoginManager

import os
from dotenv import load_dotenv

load_dotenv('.env')

app = create_app()
login_manager = LoginManager()
login_manager.init_app(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})

app.register_blueprint(EventRoutes)
app.register_blueprint(UserRoutes)
app.register_blueprint(TrashRoutes)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def index():
    return send_file('web/build/index.html')


@app.route('/discover')
def discover():
    return send_file('web/build/index.html')


@app.route("/manifest.json")
def manifest():
    return send_from_directory('web/build', 'manifest.json')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('web/build', 'favicon.ico')


@app.route('/fonts/<path:filename>')
def fonts(filename):
    return send_from_directory('web/build/fonts', filename)


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


@app.route('/update', methods=['POST'])
def update():
    if not request.json or 'ref' not in request.json:
        return jsonify({'success': False})
    if request.json['ref'] != 'refs/heads/master':
        return jsonify({'success': False})

    key = bytes(os.environ.get('UPDATE_SECRET'), 'UTF-8')
    message = bytes(json.dumps(request.json, separators=(',', ':')), 'UTF-8')

    digest = hmac.new(key, message, hashlib.sha1)
    signature = digest.hexdigest()
    if signature != request.headers.get('x-hub-signature')[5:]:
        return jsonify({'success': False})

    Popen('bash update.bash', shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
    return jsonify({'success': True})


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, threaded=True, debug=True)
