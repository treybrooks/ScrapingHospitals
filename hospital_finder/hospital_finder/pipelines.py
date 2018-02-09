# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from hospital_finder.items import HCAFinderItem, CHSFinderItem
import pymongo
import logging.handlers
from hospital_finder.settings import *
from scrapy.exceptions import DropItem

FORMAT = '%(asctime)s [%(name)s] - %(message)s'
logger = logging.getLogger(__name__)
fh = logging.handlers.RotatingFileHandler("hospital_finder_pipeline.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(fh)

class HospitalFinderPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient(
            MONGODB_SERVER,
            MONGODB_PORT
        )
        db = connection[MONGODB_DB]
        self.collection_hca = db[MONGODB_COLLECTION_hca]
        self.collection_chs = db[MONGODB_COLLECTION_chs]

    def process_item(self, item, spider):
        if isinstance(item, HCAFinderItem):
            return self.process_hca(item, spider)
        elif isinstance(item, CHSFinderItem):
            return self.process_chs(item, spider)
        else:
            return item

    def process_hca(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            self.collection_hca.insert(dict(item))
            logger.debug(
                "HCA Facility {facility} in {state} added to MongoDB database!".format(
                    facility = item['facility'],
                    state = item['state_code']
                )
            )
        return item

    def process_chs(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            self.collection_chs.insert(dict(item))
            logger.debug(
                "CHS Facility  {facility} in {state} added to MongoDB database!".format(
                    facility = item['facility'],
                    state = item['state']
                )
        )
        return item
