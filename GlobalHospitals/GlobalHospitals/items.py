# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class GlobalhospitalsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    symptom_name = Field()
    location = Field()
    offices = Field()
    summary = Field()
    related_diseases = Field()
    precaution = Field()
