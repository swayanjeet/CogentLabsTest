import requests
import time

file_id = None
FILE_PATH = "/data/test_image.JPG"
FLASK_SERVICE_URI = "http://flask-service:8080/"
UPLOAD_FILE_URI = "{}uploadFile".format(FLASK_SERVICE_URI)
QUERY_FILE_STATUS_URI = "{}queryFileStatus/".format(FLASK_SERVICE_URI)

with open(FILE_PATH, "rb") as f:
    r = requests.post(UPLOAD_FILE_URI, files={"file": f})
    print(r.json())
    file_id = r.json()["file_id"]
