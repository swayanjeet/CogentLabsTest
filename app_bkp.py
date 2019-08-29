import redis
import time
import logging
from PIL import Image
import json
import os

def get_packet_from_staging_queue():
    logging.info("Starting pop command from queue")
    packet = redis_db.lpop("STAGING_QUEUE")
    logging.info("packet is {}".format(packet))
    return packet

def process_packet(packet):
    if redis_db.sadd("PROCESSING_MAP", packet):
        logging.info("Packet not present in processing queue")
        logging.info("Processing packet")
        packet_object = json.loads(packet)
        filepath = list(packet_object.values())[0]
        resize_image(filepath)
        post_processing_steps(packet)
    else:
        logging.info("Packet present in processing queue")
        pass

def resize_image(filepath):
    logging.info("Starting file resizing")
    size = 500, 500
    im = Image.open(filepath)
    im.thumbnail(size)
    file, ext = os.path.splitext(filepath)
    im.save(file + ".thumbnail", "JPEG")
    logging.info("Completed resizing and saved files")

def post_processing_steps(packet):
    logging.info("Starting post processing steps")
    redis_db.srem("PROCESSING_MAP", packet)
    logging.info("Removing packet from processing map")
    redis_db.lpush("COMPLETION_QUEUE", packet)
    logging.info("Pushing it to completion queue")
    

logging.basicConfig(level=logging.DEBUG)
redis_db = redis.StrictRedis(host="redis", port=6379, db=0)
logging.info("Connected")


while True:
    packet = get_packet_from_staging_queue()
    if packet is not None:
        process_packet(packet)
    time.sleep(3)
