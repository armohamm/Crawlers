import urllib
import sys
import time
import re
from juicer.utils import *

class Grahak_Seva(JuicerSpider):
     name="grahak_seva"
     start_urls="http://www.grahakseva.com/?page=1"

     def __init__(self, *args, **kwargs):
          JuicerSpider.__init__(self, *args, **kwargs)
          self.cutoff_dt = None
          self.latest_dt = None
          if kwargs.get("LASTRUN"):
                self.latest_dt = get_datetime(float(kwargs.get("LASTRUN")))
          self.flag = False

     def parse(self,response):
         hdoc = HTML(response)
         raw_date = hdoc.select("//div[@class='complaints']/div[last()]/div[@class='user-meta']/text()")
         posted_date = re.findall('on[ ](.*)', textify(raw_date))[0]  ## change the name ## use findall instead of search
         posted_dt = parse_date(posted_date)

         if posted_dt > self.latest_dt:
                urls = hdoc.select_urls("//h1[@style='padding-left:10px']/a/@href", response)
                for each_url in urls:
                    yield Request(each_url, self.parse_terminal, response)
                next_page_url = hdoc.select("//div[@id='bd']/div[3]/div/span[last()]/a/@href") ## change the xpath here
                yield Request(next_page_url, self.parse, response)

     def parse_terminal(self, response):
         hdoc = HTML(response)
         author = {}
         item = Item(response)
         author_name_and_posted_date = hdoc.select("//div[@class='user-meta']/text()")## seperate the date from author name

         author_name = re.findall('(.*)[ ]on',textify(author_name_and_posted_date))[0]
	 posted_date = re.findall('on[ ](.*)',textify(author_name_and_posted_date))[0]
         author['name'] = author_name
         dt_added = parse_date(posted_date)
         item.set("dt_added", dt_added)
         complaint_title = textify(hdoc.select("//h1[@class='cpage-heading unsel']/text()"))
         author['title'] = complaint_title
         complaint_details = textify(hdoc.select("//div[@class='desc']/p/text()"))
         author['text'] = complaint_details
         item.set("author", author)
         item.set("url", response.url)
         print "--------------------------------------------"
         print item.data

