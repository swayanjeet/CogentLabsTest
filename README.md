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
   1. Redis container : This is used for storing the metadata of the images which are currently waiting to be processed, also meatdata which are currently being processed by the workers and also which have already been processed by the workers.
   2. Flask Application Container : This is used for building up the REST APIs which is exposed to User in order to submit the files, check which stage the file is in through the file_id.
   3. Worker Containers : These workers pick up the image metadata from the STAGING queue, process them (re-size the images) and then move them to a completed SET (literally a SET datastructure is implemented in Redis). Currently only 2 worker containers have been set-up for the demo.

   The below images corresponds to architectural details.
   ![Architecture Diagram](https://github.com/swayanjeet/CogentLabsTest/blob/master/docs/Architecture.png "Architecture Diagram")
   Brief Explanation of Architecture Diagram:
   
   * **Upload File API**
   1. User uploads the file through REST APIs.
   2. Flask Container receives the image and stores it in a directory.
   3. Flask Container then generates a unique file_id for the image and then forms a JSON packet containing the file_id and the path of the image. It then pushes the information into a STAGING SET AND A STAGING QUEUE simultaneously.
   4. The file_id is then returned to the User along with successfull response so that he can use the file_id to query the current stage of the file.
   5. STAGING SET is used so that all the file ids present in it can be looked up when user queries for a file.
   6. Meanwhile, the Worker containers keep polling the STAGING QUEUE. When a JSON packet is found they POP it from the STAGING QUEUE and also delete the same from the STAGING SET. After deleting it, the Worker container checks if it is already present in the PROCESSING SET. If not it adds it and starts processing. If it is already present, then some woker else might be processing it, hence current worker node drops the packet and proceeds for the next packet.
   7. PROCESSING SET is used because even if the worker containers crash messages will be retained in the PROCESSING SET.
   8. After adding the JSON packet into the PROCESSING SET, the Worker containers start processing the metadata i.e. Once they have the file_id and path of the image, they start re-sizing the images.
   9. After successfully re-sizing the image, Worker containers remove the metadata from the PROCESSING SET and add it into the COMPLETION SET so that we can have a track of which all images have been completed.
   10. The SETS are used only to keep a track of the current states of the files.
   
   * **Query Stage API**
   1. The Flask API receives the file_id and just performs a look-up on the 3 SETS. 
   2. Wherever the file_id matches, the current state of the file is returned.
   3. If file_id is not found, then "ID NOT FOUND" response is returned to the User.

- How are they connected?
   * The different containers communicate through the default network which is set up through docker compose command.
   * Only the Flask API is exposed to the outside world through port "8080" and host-ip address.
   
- What libraries/dependencies/tools did you choose and why?
   * Flask for building REST APIs because its easier to use.
   * Redis as a message queue and key value storage because it can implement a queue as well as set data structure. Also its message queue is easier to implement and can be scaled easily for handling larger loads. Apart from that we can also set up Redis slave containers pointing to the same master instance so that bottleneck will be reduced significantly in case of huge loads.
   
- Any improvements you would make to the service or tests that go beyond the scope of the assignment -
   
   * **What would need to change to put your service into production?**
   
   1. Flask would be hosted on production level server (uWSGI or apache with mod_wsgi) for production use case.
   2. Also instead of a single Flask container there would be multiple containers communicating to the same redis instance. These containers would be scaled up and down on the basis of load on the external Load Balancer. An external Load balancer would be set-up to route the requests to these Flask containers and these all orchestration and deployment can be done through Kubernetes.
   3. Apart from that we can also enable the Rolling deployment feature and health check feature of Kubernetes so as to manage the deployment and monitor the pods.
   4. Also the Redis instance needs to be upgraded to a Redis cluster so that multiples slave containers run pointing to the same master instance. This will reduce the bottleneck in case of huge loads on backend. Apart from this, we can use helm to deploy the Redis chart in Kubernetes so that scaling, orchestration and deployment becomes smooth and developers can focus on development.
   5. Apart from all this, Security has always been an important part of every Application. From the security perspective, we make sure that all the ports of the nodes are closed except the port of the Flask Application. The redis instance port needn't be exposed outside as every container inside docker-compose app can communicate with each other with the help of the default network.
   
   * **How could it be scaled up or down?**
   
   1. Autoscaling can be configured in Kubernetes deployments for both nodes as well pods. So using Kubernetes, we can deploy our application and then configure the deployment for POD as well as node autoscaling.
   
   * **How will it handle a high load of requests?**
   
   1. If the Flask Application is scaled horizontally based on the load on External Loadbalancer, then it will be able to handle the huge amount of requests. Using Kubernetes, we can configure the flask containers to be horizontally scalable automatically.
   2. The Redis instance also needs to horizontally scaled, so that it doesn't become a bottleneck in the application. We can multiple Redis slave nodes running and communicating to the same master instance. We can also configure these slave PODS(containers) to be automatically horizontally scalable. 
   
   * **What can you do to monitor and manage your services ?**
   
   1. We can use telegraf agents to collect the metrics from the containers (if deployed alone) or use the telegraf plugin for Kubernetes to collect information about the cluster. The telegraf agents can dump the metrics to Influx DB. 
   2. Also using the data from Influx DB, we can then have some dashboards in Grafana which may show when the error occured in a particular piece of code, which all packets couldn't pe processed, how many packets are waiting in the queue, how many are completed and so on. We can also have a look at the health metrics of the containers and host-machines. If we are using Kubernetes then we can have a look at the health metrics of the entire cluster and also of the individual PODs.
   3. Apart from these, we can also have a rate of processing data of different workers by calculating the length of PROCESSING QUEUE and COMPLETION QUEUE and the number of packets processed by individual workers. From this information we can also determine the average rate of processing and then scale the PODs accordingly.
   4. Also we can configure Alerts in Grafana Dashboards, so that if a container goes down because of some issue or if the memory usage is even high after being autoscaled or lets say the disk space is low then we can be notified via emails, text-messages with the help of PagerTree integration
   
   
