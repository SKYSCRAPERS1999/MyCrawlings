"""
Class definition of crawled items.
"""
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class QuestionItem(Item):
    """
    A class to store metadata of posted questions.
    """
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
    """
    A class to store main content of posted questions.
    """
    collection = "questions_test"
    q_id = Field()
    content = Field()
    # codes = Field()


class AnswerItem(Item):
    """
    A class to store answers of posted questions.
    """
    collection = "questions_test"
    q_id = Field()
    a_id = Field()
    content = Field()
    # codes = Field()
    votes = Field()
    time = Field()
    processed_time = Field()
