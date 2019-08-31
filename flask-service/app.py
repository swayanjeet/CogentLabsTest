import os
from flask import Flask, request
from werkzeug.utils import secure_filename
import logging
import redis
import datetime
import json
from ImageQueue import ImageQueue, ImageQueueException

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("FlaskService")

UPLOAD_FOLDER = "/data/uploads"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config.from_mapping(
        UPLOAD_FOLDER=UPLOAD_FOLDER
        )
image_queue = ImageQueue()

@app.route("/heartbeat")
def test():
    return {"message":"beating","STATUS":"SUCCESS"}

@app.route("/queryFileStatus/<string:file_id>", methods=["GET"])
def query_file_status(file_id):
    if request.method=="GET":
        logger.info("Inside POST request for query_file_status")
        if "file_id" is None:
            return {"message":"File id is None !!","STATUS":"FAILED"}
        else:
            current_stage = image_queue.return_current_stage_of_file(file_id)
            return {"message":current_stage,"STATUS":"SUCCESS", "file_id":file_id}

@app.route("/uploadFile", methods=["POST"])
def upload_file():
    if request.method == "POST":
        logging.info("Inside POST request")
        # check if the post request has the file part
        logger.info(str(request.files))
        if "file" not in request.files:
            logger.info("File not present in POST request")
            return {"message":"file key not found in request","STATUS":"FAILED"}
        file = request.files["file"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            logger.info("File not present")
            return {"message":"Empty file received","STATUS":"FAILED"}
        if file and allowed_file(file.filename):
            logger.info("File is {}".format(str(file)))
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            packet = dict()
            unique_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            logger.info("Unique id is {}".format(unique_id))
            packet[unique_id]=os.path.join(app.config["UPLOAD_FOLDER"], filename)
            logger.info("Image Packet is {}".format(packet))
            try:
                image_queue.insert_packet_into_staging_queue(packet)
                return {"message":"File Uploaded successfully !!","STATUS":"SUCCESS", "file_id": unique_id}
            except ImageQueueException as error:
                logger.error(error)
                return {"message":"Couldn't insert into Queue","STATUS":"FAILED"}
        else:
            return {"message":"Files other than jpg,jpeg and png are not allowed", "STATUS":"FAILED"}
            
if __name__ == "__main__":
    app.run(host="0.0.0.0",port="8080") 
