# -*- coding: utf-8 -*-
import scrapy

from selenium import webdriver
from scrapy.shell import inspect_response
import json


class ProgramListSpider(scrapy.Spider):
    name = 'program_list'
    allowed_domains = ['hackerone.com/directory/programs']
    program_list_url = 'https://hackerone.com/directory/programs/'

    custom_settings = {
        'LOG_FILE': "program_list_log.json",
    }

    def start_requests(self):
        yield scrapy.Request(self.program_list_url,
                             meta={"url_type": "program list"},
                             callback=self.parse_program_list)

    # initiate the broswer in the spider, which can be invoked in the middleware
    def __init__(self):
        # received the request from the engine and return a response to it
        # without passing through downloader
        self.options = webdriver.FirefoxOptions()
        self.options.headless = False
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

    def parse_program_list(self, response):
        program_trs = response.css('tr.spec-directory-entry')
        for program_tr in program_trs:
            program_tds = program_tr.css("td")
            # program_tds[0] ==> program column
            program_col = program_tds[0]
            program_name = program_col.css('a::text').get()
            program_url = response.urljoin(
                program_col.css('a::attr(href)').get())
            managed = True if program_col.css('span::text').get() else False
            # program_tds[1] ==> launch date column
            launch_date = program_tds[1].css("span::text").get()
            # program_tds[2] ==> reports resolved column
            rr = program_tds[2].css("span::text").get()
            # program_tds[3] ==> bounties minimum column
            b_min = program_tds[3].css('span::text').get()
            # program_tds[4] ==> bounties average column
            b_avr = program_tds[4].css('span::text').getall()
            program = {
                "name": program_name,
                "url": program_url,
                "managed": managed,
                "launch_date": launch_date,
                "reports_resolved": rr,
                "bounties_min": b_min,
                "bounties_avr": b_avr
            }
            yield program
