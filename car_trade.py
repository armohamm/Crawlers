from juicer.utils import *
import re
import time

class Car_Trade(JuicerSpider):
    name = "car_trade"
    start_urls = "http://www.cartrade.com/reviews?nav_cat=footer&nav_query=reviews"
    def __init__(self, *args, **kwargs):
        JuicerSpider.__init__(self, *args, **kwargs)
        self.cutoff_dt = None
        self.latest_dt = None
        if kwargs.get("LASTRUN"):
            self.latest_dt = get_datetime(float(kwargs.get("LASTRUN")))
        self.flag = False
    def parse(self, response):
        hdoc = HTML(response)
        raw_date_time = textify(hdoc.select("//div[@class='borderdBox popcarComp']/div[last()-2]//span[@class='rdate']/time/@datetime"))
        posted_dt = parse_date(raw_date_time)
        if posted_dt > self.latest_dt:
            urls = hdoc.select_urls("//a[@class='redd']/@href")
            for url in urls:
                yield Request(url, self.parse_terminal, response)
            next_page_url = textify(hdoc.select("//a[contains(text(),'Next')]/@href"))
            yield Request(next_page_url, self.parse, response)
        else:
            urls = hdoc.select_urls("//a[@class='redd']/@href")
            for url in urls:
                yield Request(url, self.parse_terminal, response)
    def parse_terminal(self, response):
        hdoc = HTML(response)

        review_title = textify(hdoc.select("//div[@class='span16']/h2/text()"))
        author_name_and_posted_date = textify(hdoc.select("//div[@class='borderdBox firstImpTopBox']/div/div[1]/text()"))
        an_pd = re.findall('by[ ](.*)[ ]on[ ](.*)',author_name_and_posted_date)
        review_description = textify(hdoc.select("//div[@class='borderdBox fstImprCnt']/table/tr[2]/td/div/text()"))
      
        if an_pd == []: 
           review_title = textify(hdoc.select("//div[@class='review_tab_inner']//span/text()"))
           expert_author_name = textify(hdoc.select("//span[@itemtype='http://schema.org/Review']/em/text()"))
           posted_date = textify(hdoc.select("//span[@itemtype='http://schema.org/Review']/strong/text()"))
           review_description = textify(hdoc.select("//div[@class='review_tab_inner']//p/text()"))
	   print "\n\n", review_title
           print expert_author_name, "(Expert Review)"
           print posted_date
           print review_description, "\n\n"
        else:
            author_name = an_pd[0][0]
            posted_date = an_pd[0][1]
            car_name = re.findall('.*/(.*)-user', response.url)[0]
            print "\n\n", review_title, "(", car_name, ")"
            print author_name
            print posted_date
            print review_description, "\n\n"
