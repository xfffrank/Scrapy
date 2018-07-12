# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class MeishijieItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    food_name = Field()
    cate_tags = Field()
    func_tags = Field()
    flavor = Field()
    technique = Field()
    difficulty = Field()
    persons = Field()
    main_ingre = Field()
    minor_ingre = Field()
    resource_loc = Field()
