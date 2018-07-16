# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HealthmattersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    normal_range = scrapy.Field()
    definition = scrapy.Field()
    low = scrapy.Field()
    high = scrapy.Field()
    low_drugs = scrapy.Field()
    high_drugs = scrapy.Field()
    low_states = scrapy.Field()
    high_states = scrapy.Field()
    low_causes = scrapy.Field()
    high_causes = scrapy.Field()
    url = scrapy.Field()
