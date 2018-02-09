# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HCAFinderItem(scrapy.Item):
    # define the fields for your item here like:
    facility = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    state_code = scrapy.Field()
    zip_code = scrapy.Field()
    phone = scrapy.Field()
    url = scrapy.Field()


class CHSFinderItem(scrapy.Item):
    # define the fields for your item here like:
    facility = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    url = scrapy.Field()
