# CogentLabs Test

- What API endpoints are available and how to use them ?
    * [Upload File API](docs/uploadFile.md) : `POST /uploadFile`
    * [Query File Status API](docs/queryFileStatus.md) : `GET /queryFileStatus/:file_id`
    * [Heart Beat API](docs/heartbeat.md) : `GET /heartbeat`

- How to run and test your service ?
- In order to start all the containers, clone the repository and run the below mentioned command:
      ```docker-compose up -d```
      After all the containers are up and running, run the command below to run the test script
      ```docker exec -it test_environment_cg_test python test.py```
