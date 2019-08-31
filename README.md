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
   
- An explanation of your architecture
   * The following components are present in the application:
   1. Redis container : This is used for storing the metadata of the images which are currently waiting to be processed, which are currently being processed by the workers and also which have already been processed by the workers.
   2. Flask Application Container : This used for building up the REST APIs which is exposed to User in order to submit the files, check which stage the file is in through the file_id.
   3. Worker Containers : These workers pick up the image metadata from the STAGING queue, process them (re-size the images) and then move them to a completed SET (literally a SET datastructure is implemented in Redis). Currently only 2 worker containers have been set-up for the demo.
   The below images corresponds to architectural details.
   

