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

    def return_matches(self, set_name, id):
        cursor_point, items = self.redis_db.sscan(set_name, 0, match="*{}*".format(id))
        logger.info("current cursor point : {}, items : {} for set : {}".format(cursor_point, items, set_name))
        while cursor_point != 0 and len(items)==0:
            cursor_point, items = self.redis_db.sscan(set_name, cursor_point, match="*{}*".format(id))
            logger.info("current cursor point : {}, items : {} for set : {}".format(cursor_point, items, set_name))
        logger.info("final set of matched items : {} for set {}".format(items, set_name))
        return items

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
        if len(self.return_matches(STAGING_SET_NAME, id))>0:
            return "STAGING STAGE"
        elif len(self.return_matches(PROCESSING_SET_NAME, id))>0:
            return "PROCESSING STAGE"
        elif len(self.return_matches(COMPLETION_SET_NAME, id))>0:
            return "COMPLETION STAGE"
        else:
            return "ID NOT FOUND!!"
    
if __name__=="__main__":
    image_queue = ImageQueue()
