from juicer.utils import *
import re
import time

class Sumit_Carzy(JuicerSpider):
    name = "sumit_carzy"
    start_urls = "http://www.carzy.co.in/blog/car-review/"

    def __init__(self, *args, **kwargs):
        JuicerSpider.__init__(self, *args, **kwargs)
        self.cutoff_dt = None
        self.latest_dt = None
        if kwargs.get("LASTRUN"):
            self.latest_dt = get_datetime(float(kwargs.get("LASTRUN")))
        self.flag = False
    def parse(self, response):
        hdoc = HTML(response)
        raw_date_time = textify(hdoc.select("//div[@id='content']/div[last()-1]/div[@class='postdate']/text()"))

        posted_dt = parse_date(raw_date_time)
        
        if posted_dt > self.latest_dt:
            urls = hdoc.select_urls("//div[@id='content']/div/h2/a/@href", response)
            for url in urls:
                yield Request(url, self.parse_terminal, response)
            next_page_url = textify(hdoc.select("//a[@class='nextpostslink']/@href"))
            yield Request(next_page_url, self.parse, response)
        else:
            urls = hdoc.select_urls("//div[@id='content']/div/h2/a/@href", response)
            for url in urls:
                yield Request(url, self.parse_terminal, response)

    def parse_terminal(self, response):
        hdoc = HTML(response)
        review_title = textify(hdoc.select("//div[@id='content']/div/h2/text()"))
        # author_name = textify(hdoc.select("//div[@class='postdate']/a/strong/text()"))
        posted_date = textify(hdoc.select("//div[@class='postdate']/a/strong/text() | //div[@class='postdate']/text()"))
	# complete_review = textify(hdoc.select("//div[@class='entry']//text()"))
        print "\n\n", review_title
        print "\n\n", posted_date
        # print author_name
        # print complete_review

