# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs, json, os

class Douban250Pipeline(object):
    """
    抓取中文时，若输出为json文件，默认会以 unicode 编码保存；
    这里执行的处理是将编码格式转换为 utf-8；

    还有更简单地解决办法是在 settings 中设置 FEED_EXPORT_ENCODING = 'utf-8'
    """
    def __init__(self):
        self.file = codecs.open('data_cn.json', 'w', encoding='utf-8')
        self.file.write('[\n')

    def process_item(self, item, spider):
        if item['ranking'] == '250':
            comma = ''
        else:
            comma = ','
        line = json.dumps(dict(item), ensure_ascii=False) + comma + '\n'
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.write(']')
        self.file.close()
