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
logger = logging.getLogger(__name__)

class ImageQueueException(Exception):
    pass

class ImageQueue:
    def __init__(self):
        self.redis_db = redis.StrictRedis(host="redis", port=6379, db=0)
        logger.info("Connected to Redis")

    def insert_packet_into_staging_queue(self, packet):
        logger.info("Pushing into Staging SET first")
        if self.redis_db.sadd(STAGING_SET_NAME, json.dumps(packet)):
            logger.info("Pushed packet into Staging SET")
        else:
            logger.error("Couldn't push packet {} into Staging SET".format(packet))
            raise ImageQueueException("Couldn't push packet {} into Staging SET".format(packet))

        if self.redis_db.lpush("STAGING_QUEUE", json.dumps(packet)):
            logger.info("Pushed into Staging Queue")
        else:
            logger.error("Couldn't push packet {} into Staging Queue".format(packet))
            raise ImageQueueException("Couldn't push packet {} into Staging Queue".format(packet))
        logger.info("Message packet inserted into Image Queue")

    def return_current_stage_of_file(self, id):
        logger.info("Finding packet is in which SET")
        if len(self.redis_db.sscan(STAGING_SET_NAME, 0, match="*{}*".format(id))[1])>0:
            return "STAGING STAGE"
        elif len(self.redis_db.sscan(PROCESSING_SET_NAME, 0, match="*{}*".format(id))[1])>0:
            return "PROCESSING STAGE"
        elif len(self.redis_db.sscan(COMPLETION_SET_NAME, 0, match="*{}*".format(id))[1])>0:
            return "COMPLETION STAGE"
        else:
            return "ID NOT FOUND!!"
    
if __name__=="__main__":
    image_queue = ImageQueue()
