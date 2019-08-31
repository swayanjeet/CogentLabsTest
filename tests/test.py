import requests
import time

file_id = None
FILE_PATH = "/data/test_image_new.JPG"
FLASK_SERVICE_URI = "http://flask-service:8080/"
UPLOAD_FILE_URI = "{}uploadFile".format(FLASK_SERVICE_URI)
QUERY_FILE_STATUS_URI = "{}queryFileStatus/".format(FLASK_SERVICE_URI)

with open(FILE_PATH, "rb") as f:
    r = requests.post(UPLOAD_FILE_URI, files={"file": f})
    print(r.json())
    file_id = r.json()["file_id"]

current_stage = None
while current_stage != "COMPLETION STAGE":
    r = requests.get("{}{}".format(QUERY_FILE_STATUS_URI, file_id))
    print(r.json())
    current_stage = r.json()["result"]


# Querying for a file whoose id isn't present
file_id = "2014"
r = requests.get("{}{}".format(QUERY_FILE_STATUS_URI, file_id))
print("Status Code {}, Response {}".format(r.status_code,r.json()))

# Checking file upload API if file key is not present
r = requests.post(UPLOAD_FILE_URI, files={})
print("Status Code {}, Response {}".format(r.status_code,r.json()))
