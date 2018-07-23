# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from jb9939.items import Jb9939Item
from scrapy.conf import settings
import logging

client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
db = client[settings['MONGO_DB']]
coll = db[settings['MONGO_COLL']]
logger = logging.getLogger('jb9939') 

class Jb9939Pipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, Jb9939Item):
            try:
                coll.insert(dict(item))
            except Exception as e:
                logger.warning(e)
            else:
                logger.info('%s 存储完毕', item['disease_name'])
    
    @classmethod
    def find_item(cls, name):
        return True if coll.find_one({'disease_name': name}) else False

    @classmethod
    def update(cls, name, item):
        try:
            coll.update({'disease_name': name}, {'$set': dict(item)})
        except Exception as e:
            logger.warning(e)
        else:
            logger.info('%s 更新完毕', name)
