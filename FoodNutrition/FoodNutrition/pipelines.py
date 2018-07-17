# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.conf import settings
from FoodNutrition.items import FoodnutritionItem
import pymongo

client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
db = client[settings['MONGO_DB']]
coll = db[settings['MONGO_COLL']]

class FoodnutritionPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, FoodnutritionItem):
            try:
                coll.insert(dict(item))
            except Exception as e:
                spider.logger.warning(e)
            else:
                spider.logger.info('%s 存储完毕', item['fd_name'])

    @classmethod
    def find_item(cls, name):
        return True if coll.find_one({'fd_name': name}) else False

