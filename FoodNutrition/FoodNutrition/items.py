# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class FoodnutritionItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    fd_name = Field()
    sub_category = Field()
    edible_prop = Field()
    energy = Field()
    protein = Field()
    fat = Field()
    carbohydrate = Field()
    water = Field()
    ash = Field()
    dietary_fiber = Field()
    vit_a = Field()
    carotene = Field()
    vit_b_6 = Field()
    vit_b_12 = Field()
    vit_c = Field()
    vit_e = Field()
    thiamin = Field()
    riboflavin = Field()
    niacin = Field()
    p = Field()
    k = Field()
    se = Field()
    fe = Field()
    ca = Field()
    cu = Field()
    i = Field()
    folic_acid = Field()
    zn = Field()  # 锌
    na = Field()
    mn = Field()  # 锰
    mg = Field()  # 镁
    cholesterol = Field()
    sfa = Field()  # 饱和脂肪酸
    sulfurous_fatty_acid = Field()
    aromatic_amino_acid = Field()
    mufa = Field()  # 单不饱和脂肪酸
    pufa = Field()  # 多不饱和脂肪酸
