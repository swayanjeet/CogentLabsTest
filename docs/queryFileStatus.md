# queryFileStatus

A file can be in any one of the 3 stages at a time.
- STAGING STAGE
- PROCESSING STAGE
- COMPLETION STAGE
- ID NOT FOUND !!

Used to query the current stage of a file. 

**URL** : `/queryFileStatus/:file_id`

**Method** : `GET`

**Auth required** : NO

## Success Response

**Code** : `200 OK`

**Content example**

```json
{
    "result": "COMPLETION STAGE",
    "file_id": "20190831130211396194"
}
```

## Error Response

**Condition** : If file_id is not present in request/ If file id is not found

**Code** : `400 BAD REQUEST`

**Content** :

```json
{
    "result":"File id is None !!"
}
OR
{
    "result":"ID NOT FOUND !!",
    "file_id":"2016"
}
```
