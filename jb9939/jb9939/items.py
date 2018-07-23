# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class Jb9939Item(scrapy.Item):
    # define the fields for your item here like:
    disease_name = Field()
    intro = Field()
    alias = Field()
    come_on_site = Field()
    reg_office = Field()
    infect_method = Field()
    group = Field()
    symptoms = Field()
    therapies = Field()
    clinical_exams = Field()
    medicine = Field()
