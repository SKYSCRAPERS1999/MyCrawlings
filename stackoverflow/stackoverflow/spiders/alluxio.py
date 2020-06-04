# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request

from stackoverflow.items import QuestionItem, QuestionFullItem, AnswerItem


class AlluxioSpider(scrapy.Spider):
    """
    A class to define the iteration order of crawling.

    Attributes
    ----------
    name : str
        the name of this spider class.
    allowed_domains : list
        allowed url domain of crawling
    url_template : str
        the url format of outer pages in StackOverflow's crawling

    Methods
    -------
    `start_requests(self)`:
        Initialize the starting request of crawling by `yield Request()`.

    `parse_questions(self, response)`:
        Iterate through question pages and `yields Request()` of all question posts in each page.

    `parse_answers(self, response)`:
        Crawl a question post yielded by `parse_questions` function.

    """

    name = 'alluxio'
    allowed_domains = ['stackoverflow.com']
    url_template = 'http://stackoverflow.com/search?page={page}&tab=Relevance&q={query}'

    def __init__(self, query="alluxio"):
        super().__init__()
        self.query = query

    def start_requests(self):
        """Initialize the starting request of crawling by `yield Request()`."""
        self.logger.info('start url: {}'.format(self.url_template.format(query=self.query, page=1)))
        yield Request(url=self.url_template.format(query=self.query, page=1),
                      callback=self.parse_questions,
                      meta={'page': 1})

    def parse_questions(self, response):
        """Iterate through question pages and `yields Request()` of all question posts in each page.

        Parameters
        ----------
        response: scrapy.http.Response
            HTTP response of a crawled web page.

        """
        self.logger.info('Question url: {}'.format(response.url))

        questions = response.xpath('//div[@class="question-summary search-result"]')
        page = response.meta.get('page') + 1

        if questions:
            for question in questions:
                q_item = QuestionItem()
                q_item["title"] = question.xpath('.//div[@class="result-link"]/h3/a/@title').extract_first()
                q_item['votes'] = question.xpath('.//div[@class="vote"]//span/strong/text()').extract_first()
                answer_status = question.xpath('.//div[contains(@class, "status")]/strong/text()').extract_first()
                if answer_status is None:
                    continue

                q_item["time"] = question.xpath('.//div[contains(@class, "started")]/span/@title').extract_first()
                q_item["href"] = question.xpath('.//div[@class="result-link"]/h3/a/@href').extract_first()
                q_item["href"] = response.urljoin(q_item["href"])
                q_item["q_id"] = question.xpath('./@id').extract_first()
                if q_item["q_id"].split('-') is not None:
                    q_item["q_id"] = q_item["q_id"].split('-')[-1]

                self.logger.info("QuestionItem: " + str(q_item)[:20])
                yield q_item

                yield Request(url=q_item["href"],
                              callback=self.parse_answers, meta={'q_id': q_item["q_id"]})

            yield Request(url=self.url_template.format(query=self.query, page=page),
                          callback=self.parse_questions,
                          meta={'page': page})

    def parse_answers(self, response):
        """Crawl a question post yielded by `parse_questions` function.

        Parameters
        ----------
        response: scrapy.http.Response
            HTTP response of a crawled web page.

        """
        self.logger.info('Answer url: {}'.format(response.url))

        question = response.xpath('//div[@id="mainbar"]/div[contains(@class, "question")]')
        answers = response.xpath('//div[@id="answers"]/div[contains(@class, "answer")]')
        qf_item = QuestionFullItem()
        qf_item["q_id"] = question.xpath('./@data-questionid').extract_first()
        # qf_item["codes"] = question.xpath('.//code/text()').extract()
        qf_item["content"] = question.xpath('.//div[@class="post-text"]').extract_first()

        self.logger.info("QuestionFullItem: " + str(qf_item)[:20])
        yield qf_item

        if answers:
            for answer in answers:
                a_item = AnswerItem()
                a_item["q_id"] = qf_item["q_id"]
                a_item["a_id"] = answer.xpath('./@data-answerid').extract_first()
                a_item["content"] = answer.xpath('.//div[@class="post-text"]').extract_first()
                a_item["votes"] = answer.xpath(
                    './/div[contains(@class,"votecell")]//div[contains(@class,"js-vote-count")]/@data-value').extract_first()
                # a_item["codes"] = answer.xpath('.//code/text()').extract()
                a_item["time"] = answer.xpath(
                    './/div[@class="user-action-time"]/span[@class="relativetime"]/@title').extract_first()

                self.logger.info("AnswerItem: " + str(a_item)[:20])
                yield a_item
