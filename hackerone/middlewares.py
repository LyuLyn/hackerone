# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import logging
import time

import scrapy
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.expected_conditions import \
    presence_of_element_located
from selenium.webdriver.support.ui import WebDriverWait


class HackeroneSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class HackeroneDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SeleniumDownloaderMiddleware(object):
    def restart_browser(self, spider):
        spider.browser.close()
        spider.browser.quit()
        spider.requests_count = 0
        time.sleep(5)
        spider.browser = webdriver.Firefox(options=spider.options)

    def process_request(self, request, spider):
        spider.requests_count += 1
        if spider.requests_count > spider.max_requests:
            self.restart_browser(spider)
            spider.requests_count += 1
        request_type = request.meta.get("url_type", "")
        start_time = time.time()
        finish_time = time.time()
        logging.log(logging.INFO, "Now in the SeleniumDownloaderMidderware")
        try:
            wait = WebDriverWait(spider.browser, 10)
            self.html = ""
            # if request url is the program list url
            # you should scroll the window to load all programs
            if request_type == "program list":
                spider.browser.get(request.url)
                # wait until the table loaded
                wait.until(
                    presence_of_element_located(
                        (By.CSS_SELECTOR, "table.daisy-table")))
                time.sleep(0.5)
                # starting scrolling the page
                old_page = spider.browser.page_source
                new_page = ''
                while new_page != old_page:
                    old_page = spider.browser.page_source
                    spider.browser.execute_script(
                        "window.scrollTo(0,document.body.scrollHeight)")
                    time.sleep(3)
                    new_page = spider.browser.page_source
                self.html = spider.browser.page_source
            elif request_type == "program":
                # if reqest url is program
                # you should parse it and get related thanked hackers
                spider.browser.get(request.url)
                wait.until(
                    presence_of_element_located((
                        By.XPATH,
                        "//div[@class='card__heading'][contains(.//text(),'Response Efficiency')]"
                    )))
                wait.until(
                    presence_of_element_located((
                        By.XPATH,
                        "//div[@class='card__heading'][contains(.//text(),'Program Statistics')]"
                    )))
                time.sleep(0.5)
                # obtain the program page source html
                program_page_html = spider.browser.page_source
                # jump to the top thanks url
                spider.browser.find_element_by_xpath(
                    "//a[contains(.//text(), 'Thanks')]").click()
                wait.until(
                    presence_of_element_located((
                        By.XPATH,
                        "//div[@class='card__heading'][contains(.//text(),'Thanks')]"
                    )))
                time.sleep(0.5)
                # obtain the program thanks page source html
                program_thanks_html = spider.browser.page_source
                self.html = program_page_html + program_thanks_html
                spider.current_program_count += 1
            elif request_type == "hacker":
                # if request url is hacker
                # you should parse it in detail
                spider.browser.get(request.url)
                wait.until(
                    presence_of_element_located((
                        By.XPATH,
                        "//div[@class='card__heading'][contains(.//text(),'Performance stats')]"
                    )))
                wait.until(
                    presence_of_element_located((
                        By.XPATH,
                        "//div[@class='card__heading'][contains(.//text(),'Credits')]"
                    )))
                wait.until(
                    presence_of_element_located((
                        By.XPATH,
                        "//div[@class='card__heading'][contains(.//text(),'Thanks')]"
                    )))
                time.sleep(1)
                # if there is more programs thanking the hacker, then click the view more button
                try:
                    view_more = spider.browser.find_element_by_xpath(
                        "//div[@class='card'][contains(.//text(),'Thanks')]//button"
                    )
                    while view_more:
                        old_page = spider.browser.page_source
                        view_more.click()
                        time.sleep(1)
                        new_page = spider.browser.page_source
                        while new_page == old_page:
                            time.sleep(0.5)
                            new_page = spider.browser.page_source
                        view_more = spider.browser.find_element_by_xpath(
                            "//div[@class='card'][contains(.//text(),'Thanks')]//button"
                        )
                except NoSuchElementException:
                    pass
                self.html = spider.browser.page_source
                spider.current_hacker_count += 1
            elif request_type == "program_type":
                # if reqest url is program
                # you should parse it and get related thanked hackers
                spider.browser.get(request.url)
                wait.until(
                    presence_of_element_located(
                        (By.XPATH, "//div[@class='card']")))
                time.sleep(0.5)

                # obtain the program page source html
                self.html = spider.browser.page_source
                spider.current_program_count += 1
            else:
                return None
        except TimeoutException:
            self.html = spider.browser.page_source
            # 408 ==> request timeout
            status = 408
            self.restart_browser(spider)
            time.sleep(5)
        else:
            status = 200
        finally:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            if request_type == 'hacker':
                print("%s [SeleniumMiddleware] Processing hacker count: %s" %
                      (current_time, spider.current_hacker_count))
            if request_type == 'program':
                print("%s [SeleniumMiddleware] Processing program count: %s" %
                      (current_time, spider.current_program_count))

        finish_time = time.time()
        # aumatically quit after python context manager
        time_cost = finish_time - start_time
        logging.log(logging.INFO, "TIME COST: %s seconds" % time_cost)
        return scrapy.http.HtmlResponse(url=request.url,
                                        status=status,
                                        body=self.html.encode('utf-8'),
                                        encoding='utf-8',
                                        request=request)
