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

class Worker:
    def __init__(self):
        self.redis_db = redis.StrictRedis(host="redis", port=6379, db=0)
        logging.info("Connected")
        
    def get_packet_from_staging_queue(self):
        logging.info("Starting pop command from queue")
        packet = self.redis_db.lpop(STAGING_QUEUE_NAME)
        logging.info("packet is {}".format(packet))
        if packet is not None:
            logging.info("Removing packet from STAGING SET")
            self.redis_db.srem(STAGING_SET_NAME, packet)
        return packet
    
    def process_packet(self, packet):
        if self.redis_db.sadd(PROCESSING_SET_NAME, packet):
            logging.info("Packet not present in processing queue")
            logging.info("Processing packet")
            packet_object = json.loads(packet)
            filepath = list(packet_object.values())[0]
            self.resize_image(filepath)
            self.post_processing_steps(packet)
        else:
            logging.info("Packet present in processing queue")
            pass

    def resize_image(self, filepath):
        logging.info("Starting file resizing")
        size = 500, 500
        im = Image.open(filepath)
        im.thumbnail(size)
        file, ext = os.path.splitext(filepath)
        im.save(file + ".thumbnail", "JPEG")
        logging.info("Completed resizing and saved files")

    def post_processing_steps(self, packet):
        logging.info("Starting post processing steps")
        self.redis_db.srem(PROCESSING_SET_NAME, packet)
        logging.info("Removing packet from processing SET")
        self.redis_db.sadd(COMPLETION_SET_NAME, packet)
        logging.info("Pushing it to completion SET")
    
    def __del__(self):
        self.redis_db.quit()
    
    def orchestrate(self):
        while True:
            packet = self.get_packet_from_staging_queue()
            if packet is not None:
                self.process_packet(packet)
            time.sleep(3)

if __name__=="__main__":
    worker = Worker()
    worker.orchestrate()    
