from juicer.utils import *
import re
import time
import itertools

class Sumit_Cmie(JuicerSpider):
    name = "sumit_cmie"
    start_urls = "http://www.cmie.com/"

    def __init__(self, *args, **kwargs):
        JuicerSpider.__init__(self, *args, **kwargs)
        self.cutoff_dt = None
        self.latest_dt = None
        if kwargs.get("LASTRUN"):
            self.latest_dt = get_datetime(float(kwargs.get("LASTRUN")))
        self.flag = False

    def parse(self, response):
        hdoc = HTML(response)
        all_date_time = hdoc.select("//div[contains(@class,'w270')]/div[@class='nv_dt']")
        urls = hdoc.select("//div[contains(@class,'w270')]/div[@class='i_nv_link']/a/@href")
        for each_date,each_url in zip(all_date_time,urls):
            raw_date_time = textify(each_date.select("./text()"))
            posted_dt = parse_date(raw_date_time)
            url = textify(each_url)
            if posted_dt > self.latest_dt:
                yield Request(url, self.parse_terminal, response)
    def parse_terminal(self, response):
        hdoc =HTML(response)

        review_title = textify(hdoc.select("//div[@class='article_pf']/h1/text() | //div[@class='article_pf']/h2/text()"))
        review_description = textify(hdoc.select("//div[@class='article_pf']//p/text()"))
        review_date = textify(hdoc.select("//div[@class='nv_date']/text()"))
        print "\n\n Review Title : ", review_title
        print "Review Date : ", review_date
        #print "\n\n Review Description : ", review_description
