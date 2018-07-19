# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.conf import settings
from draxe.items import DraxeItem
import pymongo
import logging

client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
db = client[settings['MONGO_DB']]
coll = db[settings['MONGO_COLL']]
logger = logging.getLogger('Draxe')  # 取到名为 Draxe 的logger实例

class DraxePipeline(object):

    def process_item(self, item, spider):
        # return item  
        if isinstance(item, DraxeItem):
            try:
                coll.insert(dict(item))
            except Exception as e:
                logger.warning(e)
            else:
                logger.info('%s 存储完毕', item['fd_name'])

    @classmethod
    def find_item(cls, name):
        return True if coll.find_one({'fd_name': name}) else False
