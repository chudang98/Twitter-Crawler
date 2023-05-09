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
CHECKPOINT_COLLECTION = global_env.CHECKPOINT_COLLECTION

utc_tz = pytz.timezone('UTC')

# Schema of checkpoint project :
#   _id : id of project ( twitter project id )
#   status : status crawling of project
#   checkpoint : last checkpoint of project
#   url : url of project
#   updated_at : last time run crawl

def get_status(project_id):
  logging.warning("Getting status of crawling project...")
  client_mongo = pymongo.MongoClient(
    MONGO_HOST
  )
  db = client_mongo[MONGO_DB]
  status = db[CHECKPOINT_COLLECTION].find_one({'_id': project_id})
  return status['status'] if status else None

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
      'updated_time': datetime.datetime.now()
    }},
    upsert=False)
  logging.warning("Updated status project.")
  client_mongo.close()
  logging.warning("Closed MongoDB Client.")

def get_checkpoint_project(project_id):
  logging.warning(f"Start get checkpoint of project {project_id}")
  logging.warning("Creating MongoDB Client...")
  client_mongo = pymongo.MongoClient(
    MONGO_HOST
  )
  db = client_mongo[MONGO_DB]
  logging.warning("Getting checkpoint from MongoDB...")
  checkpoint = db[CHECKPOINT_COLLECTION].find_one({'_id': project_id})
  logging.warning("Record checkpoint :")
  logging.warning(checkpoint)
  return checkpoint['checkpoint'] if checkpoint else None

def update_checkpoint_project(project_id, checkpoint_time=datetime.datetime.now(utc_tz)):
  logging.warning(f"Start update checkpoint of project {project_id}")
  logging.warning("Creating MongoDB Client...")
  client_mongo = pymongo.MongoClient(
    MONGO_HOST
  )
  db = client_mongo[MONGO_DB]
  db[CHECKPOINT_COLLECTION].update_one({"_id": project_id}, {"$set": {"_id": project_id, 'checkpoint': checkpoint_time, 'updated_at': datetime.datetime.now(utc_tz), 'status': 'done'}}, upsert=True)
  pass