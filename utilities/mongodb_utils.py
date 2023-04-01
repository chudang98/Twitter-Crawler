import pymongo
import logging
import sys
import os
import pytz
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + '/../')
import utilities.env_managment as global_env
import datetime
from bson.objectid import ObjectId

MONGO_HOST = global_env.MONGO_HOST
MONGO_DB = global_env.MONGO_DB
MONGO_COLLECTION = global_env.MONGO_COLLECTION


def update_status(project_id, status):
  logging.warning("Creating MongoDB Client...")
  client_mongo = pymongo.MongoClient(
    MONGO_HOST
  )
  db = client_mongo[MONGO_DB]
  db[MONGO_COLLECTION].update_one(
    {"_id": ObjectId(project_id)},
    {"$set": {
      'status': status,
      'last_run': datetime.datetime.now()
    }},
    upsert=False)
  logging.warning("Updated status project.")
  client_mongo.close()
  logging.warning("Closed MongoDB Client.")