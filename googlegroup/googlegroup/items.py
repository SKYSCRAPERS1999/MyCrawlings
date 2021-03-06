# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class QuestionItem(Item):
    """
    A class to store posted questions.
    """
    # define the fields for your item here like:
    # name = scrapy.Field()
    collection = "questions"
    q_id = Field()
    content = Field()
    title = Field()
    votes = Field()
    answers = Field()
    time = Field()
    href = Field()


class AnswerItem(Item):
    """
    A class to store posted answers.
    """
    collection = "answers"
    q_id = Field()
    a_id = Field()
    content = Field()
    codes = Field()
    votes = Field()
    time = Field()
    href = Field()
