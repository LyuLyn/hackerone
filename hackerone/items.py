# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy.item import Item, Field


class HackeroneItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ProgramItem(scrapy.Item):
    program_name = Field()
    reports_resolved = Field()
    assets_in_scope = Field()
    response_efficiency = Field()
    program_stats = Field()
    thanks_hackers = Field()


class HackerItem(scrapy.Item):
    hacker_name = Field()
    hacker_profile_url = Field()
    performance = Field()
    credit = Field()
    thanks = Field()