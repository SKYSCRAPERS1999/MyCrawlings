# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request

from stackoverflow.items import QuestionItem, AnswerItem


class AlluxioSpider(scrapy.Spider):
    name = 'alluxio'
    allowed_domains = ['stackoverflow.com']
    url_template = 'http://stackoverflow.com/search?page={page}&tab=Relevance&q={query}'

    def __init__(self, query="alluxio"):
        super().__init__()
        self.query = query

    def start_requests(self):
        self.logger.info('start url: {}'.format(self.url_template.format(query=self.query, page=1)))
        yield Request(url=self.url_template.format(query=self.query, page=1),
                      callback=self.parse_questions,
                      meta={'page': 1})

    def parse_questions(self, response):
        questions = response.xpath('//div[@class="question-summary search-result"]')
        page = response.meta.get('page') + 1

        if questions is not None:
            for question in questions:
                q_item = QuestionItem()
                q_item["title"] = question.xpath('.//div[@class="result-link"]/h3/a/@title').extract_first()
                q_item['votes'] = question.xpath('.//div[@class="vote"]//span/strong/text()').extract_first()
                q_item["answers"] = question.xpath('.//div[contains(@class, "status")]/strong/text()').extract_first()
                q_item["time"] = question.xpath('.//div[contains(@class, "started")]/span/@title').extract_first()
                q_item["href"] = question.xpath('.//div[@class="result-link"]/h3/a/@href').extract_first()
                q_item["id"] = question.xpath('./@id').extract_first()
                if q_item["id"].split('-') is not None:
                    q_item["id"] = q_item["id"].split('-')[-1]
                yield q_item

                yield Request(url=response.urljoin(q_item["href"]),
                              callback=self.parse_answers)

            yield Request(url=self.url_template.format(query=self.query, page=page),
                          callback=self.parse_questions,
                          meta={'page': page})

    def parse_answers(self, response):
        answers = response.xpath('//div[@class="answer"]')
        if answers is not None:
            for answer in answers:
                a_item = AnswerItem()
                a_item["id"] = answer.xpath('./@data-answerid').extract_first()
                a_item["content"] = answer.xpath('.//div[@class="post-text"]').extract_first()
                a_item["votes"] = answer.xpath(
                    './/div[contains(@class,"votecell")]//div[contains(@class,"js-vote-count")]/@data-value').extract_first()

                yield a_item
