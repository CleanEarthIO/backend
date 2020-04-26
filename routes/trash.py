from flask import request, jsonify, abort, Blueprint
from app import db
from models import Trash
from PIL import Image
from object_detection.utils import visualization_utils as vis_util
from detector_utils import load_inference_graph, load_image_into_numpy_array, rescale, run_inference_image

import tensorflow as tf
import numpy as np

import keras
from keras.models import Model, load_model
from keras.preprocessing import image as KerasImage
import cv2

import string
import random


TrashRoutes = Blueprint('TrashRoutes', __name__)

detection_graph, session = load_inference_graph()
MIN_THRESHOLD = 0.5

prediction_list=['cardboard', 'glass', 'trash', 'paper', 'plastic', 'trash']

# with CustomObjectScope({'relu6': ReLU,'DepthwiseConv2D': DepthwiseConv2D}):
model=load_model('trained_model.h5')
model._make_predict_function()
labels={0: 'cardboard', 1: 'glass', 2: 'trash', 3: 'paper', 4: 'plastic', 5: 'trash'}

@TrashRoutes.route('/trashAll/', methods=["GET"])
def get_all_trash():
    trash = Trash.query.all()
    return jsonify([t.serialize() for t in trash])


@TrashRoutes.route('/trash/<trash_id>', methods=["DELETE"])
def remove_trash(trash_id):
    try:
        trash = Trash.query.filter_by(id=trash_id).first()
        db.session.delete(trash)
        db.session.commit()
        return jsonify('Trash successfully deleted')
    except Exception as e:
        return str(e)


@TrashRoutes.route('/trashScan', methods=["POST"])
def scan_trash():
    if not request.form:
        return abort(400)
    
    params = ['latitude', 'longitude']

    for p in params:
        if p not in request.form:
            return abort(400)
    
    latitude = request.form['latitude']
    longitude = request.form['longitude']

    if not request.files or 'image' not in request.files:
        return abort(400)

    image = request.files['image']
    image = Image.open(image)
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
            img_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
            im.save(f"uploads/{img_id}.jpeg")

            for score, box in zip(np.nditer(output['detection_scores']), output['detection_boxes']):
                if score > MIN_THRESHOLD:
                    boxes.append(box)

    # # crop all instances of trash
    for i, box in enumerate(boxes):
        ymin, xmin, ymax, xmax = box
        im_width, im_height = image.size

        ymin = max(0, ymin-0.1)
        ymax = min(1, ymax+0.1)
        xmin = max(0, xmin-0.1)
        xmax = min(1, xmax+0.1)

        left, right, top, bottom = xmin * im_width, xmax * im_width, ymin * im_height, ymax * im_height

        zoomed_image = image.crop((left, top, right, bottom))

        zoomed_image.save("zoom"+str(i)+".jpeg")

        img = KerasImage.load_img("zoom"+str(i)+".jpeg", target_size=(300, 300))
        x = KerasImage.img_to_array(img, dtype=np.uint8)
        img=np.array(img)/255.0

        p=model.predict(img[np.newaxis, ...])
        pro=np.max(p[0], axis=-1)
        print("prob",pro)
        predicted_class = labels[np.argmax(p[0], axis=-1)]
        print("classified label:",predicted_class)

        try:
            trash = Trash(
                trash_type=predicted_class,
                latitude=latitude,
                longitude=longitude,
                image=img_id
            )
            db.session.add(trash)
            db.session.commit()
        except Exception as e:
            return str(e)

    return 'Processing'
