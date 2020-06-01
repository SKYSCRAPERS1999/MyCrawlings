"""
Downloader middleware classes for anti-crawling.
"""
# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import logging
import random
import requests

from stackoverflow.user_agent import agents


class ProxyMiddleware(object):
    """
    A class to communicate with proxy server. When a request fail several times,
    this class grabs a random proxy server and configure it as a downloader middleware
    to use for crawling.

    Methods
    -------
    get_random_proxy(self):
        Grabs a random proxy server.

    process_request(self, response, spider):
        Grabs a random proxy server and configure it as a downloader middleware to use for crawling.
    """

    def __init__(self, proxy_url):
        self.logger = logging.getLogger(__name__)
        self.proxy_url = proxy_url

    def get_random_proxy(self):
        try:
            response = requests.get(self.proxy_url)
            if response.status_code == 200:
                proxy = response.text
                return proxy
        except requests.ConnectionError:
            return False

    def process_request(self, request, spider):
        if request.meta.get('retry_times'):
            proxy = self.get_random_proxy()
            if proxy:
                uri = 'https://{proxy}'.format(proxy=proxy)
                self.logger.debug('Change Proxy to ' + proxy)
                request.meta['proxy'] = uri

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(
            proxy_url=settings.get('PROXY_URL')
        )


class RandomUserAgentMiddleware(object):
    """
    A class to randomly change the user agent in HTTP requests. It randomly choose
    a user agent from a given list and configure it as a downloader middleware.

    Methods
    -------
    process_request(self, request, spider):
        Randomly choose an user agent from `user_agent` in user_agent.py,
        and then use it to change the user agent in HTTP requests.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent
        self.logger.debug('Change UserAgent to ' + agent)
