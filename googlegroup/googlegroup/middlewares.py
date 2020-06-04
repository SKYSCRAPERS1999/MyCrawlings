# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import logging
import random
from logging import getLogger

from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from googlegroup.user_agent import agents


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

    def process_request(self, request, spider):
        request.meta['proxy'] = self.proxy_url
        self.logger.info("request.meta: {}".format(request.meta))

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


class SeleniumMiddleware:
    """A class to use the python package `Selenium` to mock a browser and crawl pages by controlling the browser. This download middleware is only enabled when `is_start` is set on Scrapy request's metadata.

    Methods
    -------
    process_request(self, request, spider):
        This function mock a browser and crawl pages by controlling the browser. First it wait for the page to crawl until fully loaded. Second it scroll down the page to load AJAX data by executing some Javascript codes. At last it return the loaded page source as Scrapy's Response for further processes.

    """
    def __init__(self, timeout=None):
        self.logger = getLogger(__name__)
        self.timeout = timeout

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.set_window_size(1400, 700)
        self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)

    def __del__(self):
        self.browser.close()

    def process_request(self, request, spider):
        if request.meta.get('is_start') is True:

            self.logger.info("Headless Chrome is Starting")
            try:
                self.browser.get("https://groups.google.com/forum/#!forum/alluxio-users")
                wait = WebDriverWait(self.browser, 1000)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'F0XO1GC-b-F')))

                elem = self.browser.find_element(By.XPATH, '//*[@class="F0XO1GC-b-F"]')

                last_height = elem.get_attribute('scrollHeight')

                for i in range(30):
                    self.browser.execute_script(
                        "document.getElementsByClassName('F0XO1GC-b-F')[0].scrollTo(0, document.getElementsByClassName('F0XO1GC-b-F')[0].scrollHeight)")

                    while elem.get_attribute('scrollHeight') == last_height:
                        continue

                    last_height = elem.get_attribute('scrollHeight')

                    self.logger.info("Scrolling Executed")

                return HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8',
                                    status=200)

            except TimeoutException:
                return HtmlResponse(url=request.url, status=500, request=request)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'))
