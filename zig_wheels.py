from juicer.utils import *
 import re
 class Zig_Wheels(JuicerSpider):
     name="zig_wheels"
     start_urls = "http://www.zigwheels.com/reviews"
 
     def parse(self,response):
         hdoc = HTML(response)
         urls = hdoc.select_urls("//a[contains(@href, 'reviews')]/@href", response)
         for url in urls:
             if "advice" in url:
                 pages_available(url,1)
             else:
                 print "other>>>", url
                 #yield Request(url,self.parse_terminal,response)
     def pages_available(url,page_no):
         hdoc = HTML(url)
         next_page_is_there = hdoc.select("//div[@class='TAR MT10 paging brdb PB15']/a[last()]/text()")
         next_page = textify(next_page_is_there)
         if next_page == "Next Page >>":
             page_no = page_no +1
             url_new = url + page_no
             yield Request(url_new, self.parse_terminal, response)
             pages_available(url,page_no)
         else:
             pass
 
     def parse_terminal(self,response):
         hdoc = HTML(response)
         author_name = hdoc.select("//div[@class='gL_12_1 postedLine']/a/text()")
         print textify(author_name)
         car_name = hdoc.select("//div[@class='PT10 brdb']/h1/text()")
         review_text=hdoc.select("//div[@class='PB15 storyText storyTextTable']/p | //div[@class='PB15 storyText storyTextTable']/p/span")
         raw_car_title = textify(car_name)
        # real_car_title = re.search('(.*):',raw_car_title) 
         print raw_car_title
         for review in review_text:
             print textify(review.select("./text()"))
