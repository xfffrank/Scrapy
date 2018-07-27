# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy.conf import settings
import logging
from GlobalHospitals.items import GlobalhospitalsItem

client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
db = client[settings['MONGO_DB']]
coll = db[settings['MONGO_COLL']]
logger = logging.getLogger('global_hospitals') 

coll_qc = db['crawled']   # 用于去重的集合
logger_qc = logging.getLogger('crawled') 

class GlobalhospitalsPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, GlobalhospitalsItem):
            if coll.find_one({'symptom_name': item['symptom_name']}):
                name = item['symptom_name']
                del item['symptom_name']
                try:
                    coll.update({'symptom_name': name}, {'$set': dict(item)})
                except Exception as e:
                    logger.warning(e)
                else:
                    logger.info('%s 更新完毕', name)
            else:
                try:
                    coll.insert(dict(item))
                except Exception as e:
                    logger.warning(e)
                else:
                    logger.info('%s 存储完毕', item['symptom_name'])

    @classmethod
    def find(cls, name='', detail_link='', yufang_link=''):
        '''
        查找数据库中是否存在相应数据

        :param str name: 症状名称
        :param str detail_link: 症状详情链接
        :param str yufang_link: 症状预防链接
        :return: 存在返回 True，不存在返回 False
        :rtype: boolean
        '''
        if name:
            return True if coll_qc.find_one({'symptom_name': name}) else False
        if detail_link:
            return True if coll_qc.find_one({'detail_link': detail_link}) else False
        if yufang_link:
            return True if coll_qc.find_one({'yufang_link': yufang_link}) else False
    
    @classmethod
    def insert(cls, item):
        '''
        插入集合

        :param dict item: 字典数据
        '''
        try:
            coll_qc.insert(item)
        except Exception as e:
            logger_qc.warning(e)
        else:
            logger_qc.debug('%s 存储完毕', item['symptom_name'])

    @classmethod
    def update(cls, name, item):
        '''
        更新集合中的文档，添加新字段

        :param name str: 症状名称
        :param item dict: 要添加的字典数据
        '''
        try:
            coll_qc.update({'symptom_name': name}, {'$set': item})
        except Exception as e:
            logger_qc.warning(e)
        else:
            logger_qc.info('%s 更新完毕', name)

    