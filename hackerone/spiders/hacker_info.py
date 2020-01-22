# -*- coding: utf-8 -*-
import scrapy
import json
import time
import shutil
import os

from hackerone.items import ProgramItem
from hackerone.items import HackerItem

from selenium import webdriver
from scrapy.shell import inspect_response


class HackerInfoSpider(scrapy.Spider):
    name = 'hacker_info'
    allowed_domains = ['hackerone.com']

    program_info_file = 'program_info.json'
    custom_settings = {
        'LOG_FILE': "hacker_info_log.json",
    }

    # initiate the broswer in the spider, which can be invoked in the middleware
    def __init__(self):
        # received the request from the engine and return a response to it
        # without passing through downloader
        self.options = webdriver.FirefoxOptions()
        self.options.headless = True
        self.browser = webdriver.Firefox(options=self.options)
        self.browser.set_page_load_timeout(30)

        self.requests_count = 0
        # 30 ===> about 1000 MB Memory
        # 50 ===> about 1400 MB Memory
        # 100 ===> about 3100 MB Memory
        self.max_requests = 80
        self.current_program_count = 0
        self.current_hacker_count = 0
        super().__init__()

    # close the browser when the spider are closed.
    def close(self):
        self.browser.quit()

    def start_requests(self):
        with open(self.program_info_file, 'r') as f:
            self.programs = json.load(f)
        hackers_thanked = []
        for program in self.programs:
            hackers_thanked.extend(program.get("thanks_hackers"))
        self.hackers_thanked_url_list = list(
            set([hacker.get("profile_url") for hacker in hackers_thanked]))
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("%s [JOEYLYU] %s hackers detected" %
              (current_time, len(self.hackers_thanked_url_list)))
        for hacker_url in self.hackers_thanked_url_list:
            yield scrapy.Request(hacker_url,
                                 meta={'url_type': 'hacker'},
                                 callback=self.parse_hacker_info)

    def parse_hacker_info(self, response):
        # inspct response by invoking scrapy shell
        # inspect_response(response, self)
        name = response.css("strong::text").get()
        # parse Performance Stats card
        performance_stats = response.xpath(
            "//div[@class='card'][contains(.//text(),'Performance stats')]"
        ).css('span::text').getall()
        performance = [{
            x: y
        } for x, y in zip(performance_stats[1::2], performance_stats[::2])
                       ] if performance_stats else None
        # Parse Credit card
        credit_stats = response.xpath(
            "//div[@class='card'][contains(.//text(),'Credit')]").css(
                'span::text').getall()
        credit = [{
            x: y
        } for x, y in zip(credit_stats[1::2], credit_stats[::2])
                  ] if credit_stats else None
        # Parse Thanks card
        thanks_items = response.xpath(
            "//div[@class='card'][contains(.//text(),'Thanks')]").css(
                'div.spec-thanks-item')
        thanks = []
        for thanks_item in thanks_items:
            div_text = thanks_item.css("div::text").getall()
            span_text = thanks_item.css("span::text").getall()
            if ' ' in div_text:
                div_text.remove(' ')
            thanks_item_info = span_text
            thanks_item_info[2:2] = div_text
            thanks_item_info[0:3] = [
                thanks_item_info[0] + thanks_item_info[1] + thanks_item_info[2]
            ]
            program_name = thanks_item.css('a::text').get()
            program_url = thanks_item.css('a::attr(href)').get()
            thanks.append({
                "program_name": program_name,
                "program_url": program_url,
                "valid_closed_report": thanks_item_info[0],
                "reputation": thanks_item_info[1],
                "rank": thanks_item_info[2]
            })

        yield HackerItem(hacker_name=name,
                         hacker_profile_url=response.url,
                         performance=performance,
                         credit=credit,
                         thanks=thanks)
