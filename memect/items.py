# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class MemectItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    # str type
    author_name = Field()
    # str type
    author_page_url = Field()
    # str type
    author_img_url = Field()
    # str type
    pub_time = Field()
    # list type
    keywords = Field()
    # str type
    content_text = Field()
    # str type
    content_page_url = Field()
    # str type
    content_img_url = Field()
    # str type
    site_type = Field()
