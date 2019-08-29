import redis
import time
import logging

logging.basicConfig(level=logging.DEBUG)
redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)
logging.info("Connected")
while True:
    logging.info("Trying to run this app")
    time.sleep(3)
