import hashlib
import hmac
import json

from flask import request, jsonify, send_file, send_from_directory
from app import create_app
from flask_cors import CORS
from auth import AuthError
from routes import EventRoutes, UserRoutes, TrashRoutes
from subprocess import Popen

import tensorflow as tf
import numpy as np
from PIL import Image
from object_detection.utils import ops as utils_ops
from object_detection.utils import visualization_utils as vis_util

from detector_utils import load_inference_graph, load_image_into_numpy_array, rescale, run_inference_image

import os
from dotenv import load_dotenv

load_dotenv('.env')

app = create_app()
cors = CORS(app, resources={r"*": {"origins": "*"}})

app.register_blueprint(EventRoutes)
app.register_blueprint(UserRoutes)
app.register_blueprint(TrashRoutes)

detection_graph, session = load_inference_graph()
MIN_THRESHOLD = 0.5

@app.route('/')
def index():
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
@app.route('/trashScan', methods=["GET"])
def scan_trash():
    # TODO get image, longitude, latitude from request

    image = Image.open('test.jpg')
    image = image.convert('RGB')
    im_width, im_height = image.size
    if im_width > 640 or im_height > 640:
        image = rescale(im_width, im_height, image)

    image_np = load_image_into_numpy_array(image)

    boxes = []

    with detection_graph.as_default():             
        with tf.device('/device:CPU:0'):
            output = run_inference_image(image_np, session)
            vis_util.visualize_boxes_and_labels_on_image_array(
                image_np,
                output['detection_boxes'],
                output['detection_classes'],
                output['detection_scores'],
                {0: {'name': 'not litter'}, 1: {'name': 'litter'}},
                instance_masks=output.get('detection_masks'),
                use_normalized_coordinates=True,
                max_boxes_to_draw=30,
                min_score_thresh=MIN_THRESHOLD,
                line_thickness=2)
            im = Image.fromarray(image_np)
            im.save("save.jpeg")

            #remove this later
            for score, box in zip(np.nditer(output['detection_scores']), output['detection_boxes']):
                if score > MIN_THRESHOLD:
                    boxes.append(box)

    trash_images = []
    for i, box in enumerate(boxes):
        ymin, xmin, ymax, xmax = box
        im_width, im_height = image.size

        ymin = max(0, ymin-0.05)
        ymax = min(1, ymax+0.05)
        xmin = max(0, xmin-0.05)
        xmax = min(1, xmax+0.05)

        left, right, top, bottom = xmin * im_width, xmax * im_width, ymin * im_height, ymax * im_height
        trash_images.append(image.crop((left, top, right, bottom)))

        trash_images[i].save("zoom"+str(i)+".jpeg")

    # get all instances of trash in the image
    # crop all instances of trash and classify what type of trash it is
    # add all the trash to the db
    return jsonify({'numberOfTrash': num_trash})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
