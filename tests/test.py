import requests

with open('/data/Declaration_new.jpg', 'rb') as f:
    r = requests.post('http://flask-service:8080/uploadFile', files={'file': f})
    print(r.json())

with open('/data/Declaration_new.jpg', 'rb') as f:
    r = requests.post('http://flask-service:8080/uploadFile', files={})
    print(r.json())

with open('/data/Declaration_new.jpg', 'rb') as f:
    r = requests.post('http://flask-service:8080/uploadFile', files={'file': None})
    print(r.json())

