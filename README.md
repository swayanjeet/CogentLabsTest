# CogentLabs Test

- What API endpoints are available and how to use them ?
    * [Upload File API](docs/uploadFile.md) : `POST /uploadFile`
    * [Query File Status API](docs/queryFileStatus.md) : `GET /queryFileStatus/:file_id`
    * [Heart Beat API](docs/heartbeat.md) : `GET /heartbeat`

- How to run and test your service ?
   * In order to start all the containers, clone the repository and run the below mentioned command 
   ```
   docker-compose up -d
   ```
   * After all the containers are up and running, run the command below to run the test script
   ```
   docker exec -it test_environment_cg_test python test.py
   ```
   This will run 4 test cases in order to test if the api is running properly or not.
   They are :
   1. It will try upload a file through the upload API.
   2. Then it will check the current stages of file until the file reaches COMPLETION STAGE
   3. It will query for the status of a file which is non existent and the API should return "ID NOT FOUND !!"
   4. It will try sending a request without file key in it and check if API returns "file key not found in request"
   
- An explanation of the architecture
   * The following components are present in the application:
   1. Redis container : This is used for storing the metadata of the images which are currently waiting to be processed, which are currently being processed by the workers and also which have already been processed by the workers.
   2. Flask Application Container : This used for building up the REST APIs which is exposed to User in order to submit the files, check which stage the file is in through the file_id.
   3. Worker Containers : These workers pick up the image metadata from the STAGING queue, process them (re-size the images) and then move them to a completed SET (literally a SET datastructure is implemented in Redis). Currently only 2 worker containers have been set-up for the demo.

   The below images corresponds to architectural details.
   ![Architecture Diagram](https://github.com/swayanjeet/CogentLabsTest/blob/master/docs/Architecture.png "Architecture Diagram")
   Brief Explanation of Architecture Diagram:
   * Upload File API
   1. User uploads the file through REST APIs.
   2. Flask Container receives the image and stores it in a directory.
   3. Flask Container then generates a unique file_id for the image and then forms a JSON packet containing the file_id and the path of the image. It then pushes the information into a STAGING SET AND A STAGING QUEUE simultaneously.
   4. The file_id is then returned to the User along with successfull response so that he can use the file_id to query the current stage of the file.
   5. STAGING SET is used so that all the file ids present in it can be looked up when user queries for a file.
   6. Meanwhile, the Worker containers keep polling the STAGING QUEUE. When a JSON packet is found they POP it from the STAGING QUEUE and also delete the same from the STAGING SET. After deleting it, the Worker container checks if it is already present in the PROCESSING SET. If not it adds it and starts processing. If it is already present, then someone else might be processing it, hence current worker node drops the packet and proceeds for the next packet.
   7. PROCESSING SET is used because even if the worker containers crash messages will be retained in the PROCESSING SET.
   8. After adding the JSON packet into the PROCESSING SET, the Worker containers start processing the metadata i.e. Once they have the file_id and path of the image, they start re-sizing the images.
   9. After successfully re-sizing the image, Worker containers remove the metadata from the PROCESSING SET and add it into the COMPLETION SET so that we can have a track of which all images have been completed.
   10. The SETS are used only to keep a track of the current states of the files.
