# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.conf import settings
from HealthMatters.items import HealthmattersItem

class HealthmattersPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        db = client[settings['MONGO_DB']]
        self.coll = db[settings['MONGO_COLL']]

    def process_item(self, item, spider):
        if isinstance(item, HealthmattersItem):
            # format_item = dict(item)
            try:
                self.coll.insert(dict(item))  # 需显式转化成字典，否则需要定义 _id 字段
            except Exception as e:
                spider.logger.warning(e)
            else:
                spider.logger.info('%s 存储完毕', item['title'])
            # return item  # 在控制台输出 item
