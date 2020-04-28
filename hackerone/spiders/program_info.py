# -*- coding: utf-8 -*-
import scrapy
import json
from hackerone.items import ProgramItem
from selenium import webdriver
from scrapy.shell import inspect_response


class ProgramInfoSpider(scrapy.Spider):
    name = 'program_info'
    allowed_domains = ['hackerone.com']

    program_list_file = "program_list.json"
    custom_settings = {
        'LOG_FILE': "program_info_log.json",
    }

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

    def start_requests(self):
        with open(self.program_list_file, 'r') as f:
            self.programs = json.load(f)

        for program in self.programs:
            yield scrapy.Request(program.get("url"),
                                 meta={'url_type': 'program', 
                                 'program_name': program.get("name")},
                                 callback=self.parse_program_info)

    # parse the data about the program
    def parse_program_info(self, response):
        # inspct response by invoking scrapy shell
        # inspect_response(response, self)
        [program_response, program_thanks_reponse] = response.css("html")
        # extract information from the program page
        intro = program_response.css("div.card")[0].css(
            "div.daisy-helper-text::text").getall()
        name = program_response.css("h1::text").get()
        reports_resolved = program_response.css(
            "strong span::text").get() if 'Reports resolved' in intro else None
        assets_in_scope = program_response.css("strong.daisy-text::text").get(
        ) if 'Assets in scope' in intro else None
        # parse the Response Efficiency card
        response_efficiency = program_response.xpath(
            "//div[@class='card'][contains(.//text(),'Response Efficiency')]"
        ).css("span::text").getall()
        response_efficiency_formatted = [{
            x: y
        } for x, y in zip(response_efficiency[1::2], response_efficiency[::2])]
        # parse the number of qualified reports
        qualified_ratio = program_response.css(
            'div.spec-response-efficiency-percentage::text').get()
        dataset = program_response.css('small::text').get()
        response_efficiency_formatted.append(
            {"%s %s" % ("Qualified Reports", dataset): qualified_ratio
             }) if qualified_ratio and dataset else None
        # parse the Program Statistics card
        program_stats = program_response.xpath(
            "//div[@class='card'][contains(.//text(),'Program Statistics')]"
        ).css("span::text").getall()
        # when " - " is in the list, it means that you should
        # concatenate the item before and after this item
        while ' - ' in program_stats:
            index = program_stats.index(' - ')
            program_stats[index - 1:index + 2] = [
                program_stats[index - 1] + program_stats[index] +
                program_stats[index + 1]
            ]
        program_stats_formatted = [{
            x: y
        } for x, y in zip(program_stats[1::2], program_stats[::2])]
        # extract information from thanks page
        thanks = program_thanks_reponse.css("div.card")[-1].css(
            'strong::text').getall()
        if thanks:
            [thanks_hacker_rank,
             thanks_hacker_name] = [thanks[::2], thanks[1::2]]
            thanks_hacker_url = program_thanks_reponse.css("div.card")[-1].css(
                'a::attr(href)').getall()
            # construct a dict to store the info of thanked hackers
            thanks_hackers = [{
                "rank": hacker_rank,
                "name": hacker_name,
                "profile_url": response.urljoin(hacker_url)
            } for hacker_rank, hacker_name, hacker_url in zip(
                thanks_hacker_rank, thanks_hacker_name, thanks_hacker_url)]
        else:
            thanks_hackers = []
        # construct the program item using the extracted data
        yield ProgramItem(program_name=name,
                          reports_resolved=reports_resolved,
                          assets_in_scope=assets_in_scope,
                          response_efficiency=response_efficiency_formatted,
                          program_stats=program_stats_formatted,
                          thanks_hackers=thanks_hackers)
