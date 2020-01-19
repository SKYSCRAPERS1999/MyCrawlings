# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class QuestionItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = Field()
    title = Field()
    votes = Field()
    answers = Field()
    description = Field()
    time = Field()
    href = Field()


class AnswerItem(Item):
    id = Field()
    content = Field()
    votes = Field()
    time = Field()
    name = Field()
