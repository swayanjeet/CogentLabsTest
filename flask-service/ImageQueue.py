import redis
import time
import logging
import json
import os

PROCESSING_SET_NAME = "PROCESSING_SET"
STAGING_QUEUE_NAME = "STAGING_QUEUE"
COMPLETION_SET_NAME = "COMPLETION_SET"
STAGING_SET_NAME = "STAGING_SET"

logging.basicConfig(level=logging.DEBUG)

class ImageQueue:
    def __init__(self):
        self.redis_db = redis.StrictRedis(host="redis", port=6379, db=0)
        logging.info("Connected to Redis")
        
    def insert_image_into_staging_queue(self, packet):
        logging.info("Pushing into Staging SET first")
        self.redis_db.sadd(STAGING_SET_NAME, json.dumps(packet))
        logging.info("Pushing into Staging Queue")
        self.redis_db.lpush("STAGING_QUEUE", json.dumps(packet))
        logging.info("Message packet inserted into Redis Queue")
    
    def return_current_stage_of_file(self, id):
        logging.info("Checking if present in Processing SET")
        if len(self.redis_db.sscan(STAGING_SET_NAME, 0, match="*{}*".format(id))[1])>0:
            return "STAGING STAGE"
        elif len(self.redis_db.sscan(PROCESSING_SET_NAME, 0, match="*{}*".format(id))[1])>0:
            return "PROCESSING STAGE"
        elif len(self.redis_db.sscan(COMPLETION_SET_NAME, 0, match="*{}*".format(id))[1])>0:
            return "COMPLETION STAGE"
        else:
            return "ID NOT FOUND!!"

    def __del__(self):
        self.redis_db.quit()

if __name__=="__main__":
    image_queue = ImageQueue()
