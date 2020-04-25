from flask import request, jsonify, abort, Blueprint
from app import db
from models import Trash

import tensorflow as tf
import numpy as np
from PIL import Image
from object_detection.utils import ops as utils_ops
from object_detection.utils import visualization_utils as vis_util

# import keras
# from keras.models import Model, load_model
# from keras.applications import mobilenet
# from keras.applications.mobilenet import preprocess_input
# from keras.preprocessing import image as KerasImage
# from keras.utils.generic_utils import CustomObjectScope
# import cv2

from detector_utils import load_inference_graph, load_image_into_numpy_array, rescale, run_inference_image



TrashRoutes = Blueprint('TrashRoutes', __name__)

detection_graph, session = load_inference_graph()
MIN_THRESHOLD = 0.5

# prediction_list=['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']
# model=load_model('model1.h5', custom_objects={'relu6': mobilenet.relu6})


@TrashRoutes.route('/trashAll/', methods=["GET"])
def get_all_trash():
    trash = Trash.query.all()
    return jsonify([t.serialize() for t in trash])


@TrashRoutes.route('/trash', methods=["POST"])
def create_trash():
    if not request.json:
        return abort(400)

    params = ['trash_type', 'latitude', 'longitude']

    for p in params:
        if p not in request.json:
            return abort(400)

    trash_type = request.json['trash_type']
    latitude = request.json['latitude']
    longitude = request.json['longitude']

    try:
        trash = Trash(
            trash_type=trash_type,
            latitude=latitude,
            longitude=longitude
        )
        db.session.add(trash)
        db.session.commit()
        return jsonify(trash.serialize())
    except Exception as e:
        return str(e)


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
    # image = Image.open('test.jpg')
    image = image.convert('RGB')
    im_width, im_height = image.size
    if im_width > 640 or im_height > 640:
        image = rescale(im_width, im_height, image)

    image_np = load_image_into_numpy_array(image)


    # get all instances of trash in the image
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

            for score, box in zip(np.nditer(output['detection_scores']), output['detection_boxes']):
                if score > MIN_THRESHOLD:
                    boxes.append(box)

    for box in boxes:
        try:
            trash = Trash(
                trash_type='trash',
                latitude=latitude,
                longitude=longitude
            )
            db.session.add(trash)
            db.session.commit()
        except Exception as e:
            return str(e)

    # # crop all instances of trash
    # for i, box in enumerate(boxes):
    #     ymin, xmin, ymax, xmax = box
    #     im_width, im_height = image.size

    #     ymin = max(0, ymin-0.05)
    #     ymax = min(1, ymax+0.05)
    #     xmin = max(0, xmin-0.05)
    #     xmax = min(1, xmax+0.05)

    #     left, right, top, bottom = xmin * im_width, xmax * im_width, ymin * im_height, ymax * im_height

    #     zoomed_image = image.crop((left, top, right, bottom))

    #     zoomed_image.save("zoom"+str(i)+".jpeg")

    #     img = KerasImage.load_img("zoom"+str(i)+".jpeg", target_size=(224, 224))
    #     x = KerasImage.img_to_array(img)
    #     x = np.expand_dims(x, axis=0)
    #     x = preprocess_input(x)

    #     pred_img = np.asarray(x)
        

    #     yo = model.predict(pred_img)
    #     pred = prediction_list[np.argmax(yo)]

    #     cv2.putText(img, pred, (10,1000), cv2.FONT_HERSHEY_SIMPLEX, 5, (0,0,0), 5, False)
    #     name='img'+str(i)+'.png'
    #     cv2.imwrite(os.path.join('prediction_images', name), img)

    
    # classify what type of trash it is

    # add all the trash to the db
    return 'Processing'


# @TrashRoutes.route('/trashScan', methods=["POST"])
# def scan_trash():
#     # get image, longitude, latitude from request
#     # get all instances of trash in the image
#     # crop all instances of trash and classify what type of trash it is
#     # add all the trash to the db
#     return 'todo'
