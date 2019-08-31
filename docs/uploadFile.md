# uploadFile

Used to upload images to a message Queue

**URL** : `/uploadFile`

**Method** : `POST`

**Auth required** : NO


## Success Response

**Code** : `200 OK`

**Content example**

```python
import requests

with open(FILE_PATH, "rb") as f:
    r = requests.post(UPLOAD_FILE_URI, files={"file": f})
```

## Error Response

**Condition** : If file key is not present/empty file is received

**Code** : `400 BAD REQUEST`

**Content** :

```json
{
    "result":"file key not found in request"
}
OR
{
    "result":"Empty file received"
}
```