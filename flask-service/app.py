import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import logging
import redis
import datetime
import json

logging.basicConfig(level=logging.DEBUG)

UPLOAD_FOLDER = "/data/uploads"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def insert_image_into_processing_queue(packet):
    r = redis.Redis(host='redis', port=6379, db=0)
    logging.info("Redis connected")
    r.lpush("STAGING_QUEUE", json.dumps(packet))
    logging.info("Message packet inserted into Redis")

app = Flask(__name__)
app.config.from_mapping(
        UPLOAD_FOLDER=UPLOAD_FOLDER
        )
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#app = Flask(__name__)
@app.route('/')
def test():
    return "Hello"

@app.route('/uploadFile', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        logging.info("Inside POST request")
        # check if the post request has the file part
        logging.info(str(request.files))
        if 'file' not in request.files:
            logging.info("File not present in POST request")
            return "No Files in request"
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            logging.info("File not present")
            return "No Selected File"
        if file and allowed_file(file.filename):
            logging.info("File is {}".format(str(file)))
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            packet = dict()
            unique_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
            logging.info("Unique id is {}".format(unique_id))
            packet[unique_id]=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            logging.info("Image Packet is {}".format(packet))
            insert_image_into_processing_queue(packet)
            return "File Uploaded"

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='8080')
