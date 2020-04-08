# -*- coding: utf-8 -*-
import scrapy
import json
from hackerone.items import ProgramTypeItem
from selenium import webdriver
from scrapy.shell import inspect_response


class ProgramInfoSpider(scrapy.Spider):
    name = 'program_type'
    allowed_domains = ['hackerone.com']

    program_list_file = "program_list.json"
    custom_settings = {
        'LOG_FILE': "program_type_log.json",
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
        with open(self.program_list_file, 'r') as f:
            self.programs = json.load(f)
        self.program_urls = [program.get("url") for program in self.programs]
        for program_url in self.program_urls:
            yield scrapy.Request(program_url,
                                 meta={'url_type': 'program_type'},
                                 callback=self.parse_program_type)

    # parse the program type
    def parse_program_type(self, response):
        # inspct response by invoking scrapy shell
        # inspect_response(response, self)

        program_name = response.css("h1::text").get()
        program_type = -1
        program_info = response.css(
            "div.card div.better-profile-header__program-type strong::text"
        ).get()
        if "Vulnerability Disclosure Program" in program_info:
            program_type = 0
        elif "Bug Bounty Program" in program_info:
            program_type = 1

        yield ProgramTypeItem(program_name=program_name,
                              program_type=program_type)
