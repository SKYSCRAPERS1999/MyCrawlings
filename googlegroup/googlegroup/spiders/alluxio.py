# -*- coding: utf-8 -*-
import os
import re

import scrapy
from bs4 import BeautifulSoup
from scrapy import Request

from googlegroup.items import QuestionItem, AnswerItem


class AlluxioSpider(scrapy.Spider):
    name = 'alluxio'
    allowed_domains = ['groups.google.com']
    base_url = 'https://groups.google.com/forum'

    def start_requests(self):
        start_url = 'https://groups.google.com/forum/#!forum/alluxio-users'
        yield Request(url=start_url, callback=self.parse, meta={'is_start': True})

    def parse(self, response):
        post_items = response.xpath('//div[@class="F0XO1GC-rb-h"]')
        for post_item in post_items:
            post_count = post_item.xpath('.//span[@class="F0XO1GC-rb-r"]/text()').extract_first()
            if re.match('1 post', post_count):
                continue

            post_href = post_item.xpath('.//a[@class="F0XO1GC-q-R"]/@href').extract_first()
            post_href = '{}/{}'.format(self.base_url, post_href)
            self.logger.info("href: {} with {}".format(post_href, post_count))
            yield Request(url=post_href, callback=self.parse_post)

    def parse_post(self, response):
        self.logger.info("Response: " + str(response.url))
        # soup = BeautifulSoup(response.body, 'html.parser')
        # self.logger.info("Post: " + str(soup.prettify()))
        # return

        title = response.xpath('//head/title/text()').extract_first()
        url = response.xpath('//head/link/@href').extract_first()
        post_id = os.path.split(url)[-1]

        posts = response.xpath('//body//table/tr')

        times = []
        texts = []
        hrefs = []

        for post in posts:
            time = post.xpath('.//td[@class="lastPostDate"]/text()').extract_first()
            text = post.xpath('.//td[@class="snippet"]/div/div/div[@dir="ltr"]').extract_first()
            href = post.xpath('.//td[@class="subject"]/a/@href').extract_first()
            times.append(time)
            texts.append(text)
            hrefs.append(href)

        q_item = QuestionItem()
        q_item['q_id'] = post_id
        q_item['title'] = title
        q_item['time'] = times[0]
        q_item['href'] = url
        q_item['content'] = texts[0]
        self.logger.info("QuestionItem: " + str(q_item))
        yield q_item

        for i in range(1, len(posts)):
            a_item = AnswerItem()
            a_item['q_id'] = post_id
            a_item['a_id'] = "{}_{}".format(post_id, i)
            a_item['content'] = texts[i]
            a_item['time'] = times[i]
            a_item['href'] = hrefs[i]
            self.logger.info("AnswerItem: " + str(a_item))
            yield a_item
