import redis
import time
import logging
from PIL import Image
import json
import os

PROCESSING_SET_NAME = "PROCESSING_SET"
STAGING_QUEUE_NAME = "STAGING_QUEUE"
COMPLETION_SET_NAME = "COMPLETION_SET"
STAGING_SET_NAME = "STAGING_SET"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("Worker")

class WorkerDataException(Exception):
    pass

class Worker:
    def __init__(self):
        self.redis_db = redis.StrictRedis(host="redis", port=6379, db=0)
        logger.info("Connected to Redis")
        
    def get_packet_from_staging_queue(self):
        #logger.info("Starting pop command from queue")
        packet = self.redis_db.lpop(STAGING_QUEUE_NAME)
        #logger.info("packet is {}".format(packet))
        if packet is not None:
            logger.info("Removing packet from STAGING SET")
            if self.redis_db.srem(STAGING_SET_NAME, packet):
                logger.info("Removed packet from STAGING SET")
            else:
                logger.error("Could not remove packet {} from STAGING SET".format(packet))
                raise WorkerDataException("Could not remove packet {} from STAGING SET".format(packet))
        return packet
    
    def process_packet(self, packet):
        if self.redis_db.sadd(PROCESSING_SET_NAME, packet):
            logger.info("Packet not present in processing queue")
            logger.info("Processing packet")
            packet_object = json.loads(packet)
            filepath = list(packet_object.values())[0]
            logger.info("File path present in packet is {}".format(filepath))
            self.resize_image(filepath)
            self.post_processing_steps(packet)
        else:
            logger.info("Packet present in processing queue")
            pass

    def resize_image(self, filepath):
        logger.info("Starting file resizing to size 500 * 500")
        size = 500, 500
        try:
            im = Image.open(filepath)
            im.thumbnail(size)
            file, ext = os.path.splitext(filepath)
            im.save(file + ".thumbnail", "JPEG")
            logger.info("Completed resizing and saved file")
        except IOError as error:
            logger.error("Filepath {} not found while re-sizing image".format(filepath))
            raise error
        except ValueError as error:
            logger.error("Couldn't save file after resizing original file {} !!".format(filepath))
            raise error

    def post_processing_steps(self, packet):
        logger.info("Starting post processing steps")
        if self.redis_db.srem(PROCESSING_SET_NAME, packet):
            logger.info("Removed packet from processing SET")
        else:
            logger.error("Couldn't remove packet {} from processing SET".format(packet))
            raise WorkerDataException("Couldn't remove packet {} from processing SET".format(packet))
        if self.redis_db.sadd(COMPLETION_SET_NAME, packet):
            logger.info("Pushed it to completion SET")
        else:
            logger.error("Couldn't push packet {} to Completion SET".format(packet))
            raise WorkerDataException("Couldn't remove packet {} from processing SET".format(packet))
    
    def orchestrate(self):
        while True:
            try:
                packet = self.get_packet_from_staging_queue()
                if packet is not None:
                    self.process_packet(packet)
            except WorkerDataException as error:
                continue
            except IOError as error:
                continue
            except ValueError as error:
                continue


if __name__=="__main__":
    worker = Worker()
    worker.orchestrate()    
