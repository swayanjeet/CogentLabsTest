# uploadFile

Used to uploadFiles to a message Queue

**URL** : `/uploadFile`

**Method** : `POST`

**Auth required** : NO

**Data constraints**

```Multipart form data
```

## Success Response

**Code** : `200 OK`

**Content example**

```json
{
    "message": "File Uploaded successfully !!",
    "file_id": "20195667987090"
}
```

## Error Response

**Condition** : If file key is not present/empty file is received

**Code** : `400 BAD REQUEST`

**Content** :

```json
{
    "message":"file key not found in request"
}
OR
{
    "message":"Empty file received"
}
```
