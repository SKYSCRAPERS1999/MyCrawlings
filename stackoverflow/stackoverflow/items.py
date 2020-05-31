# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class QuestionItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    collection = "questions_test"
    q_id = Field()
    title = Field()
    votes = Field()
    answers = Field()
    time = Field()
    href = Field()
    processed_time = Field()


class QuestionFullItem(Item):
    collection = "questions_test"
    q_id = Field()
    content = Field()
    # codes = Field()


class AnswerItem(Item):
    collection = "questions_test"
    q_id = Field()
    a_id = Field()
    content = Field()
    # codes = Field()
    votes = Field()
    time = Field()
    processed_time = Field()
