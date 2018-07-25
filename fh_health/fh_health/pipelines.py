# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy.conf import settings
import logging
from fh_health.items import FhHealthItem

client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
db = client[settings['MONGO_DB']]
coll = db[settings['MONGO_COLL']]
logger = logging.getLogger('fh_health') 

class FhHealthPipeline(object):
    def process_item(self, item, spider):
        return item

    @classmethod
    def find_item(cls, name):
        return True if coll.find_one({'symptom_name': name}) else False

    @classmethod
    def insert(cls, item):
        try:
            coll.insert(item)
        except Exception as e:
            logger.warning(e)
        else:
            logger.debug('%s 存储完毕', item['symptom_name'])

    @classmethod
    def update(cls, name, item):
        try:
            coll.update({'symptom_name': name}, {'$set': item})
        except Exception as e:
            logger.warning(e)
        else:
            logger.info('%s 更新完毕' % name)
    
