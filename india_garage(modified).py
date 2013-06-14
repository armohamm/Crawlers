#code to crawl the complete website based on the date and time of the posts
#each time the date and time of the posts falls with in the range of LASTRUN
#the post is crawled
#its working 100% fine and efficient than the previous one
from juicer.utils import *
import re
import time
class India_Garage(JuicerSpider):
    name = "india_garage"
    start_urls = "http://www.indiagarage.com/forum.php"

    def __init__(self, *args, **kwargs):
        JuicerSpider.__init__(self, *args, **kwargs)
        self.cutoff_dt = None
        self.latest_dt = None
        if kwargs.get("LASTRUN"):
            self.latest_dt = get_datetime(float(kwargs.get("LASTRUN")))
        self.flag = False

    def parse(self, response):
        hdoc = HTML(response)
        advice_page_urls = hdoc.select_urls("//h2[@class='forumtitle']/a[contains(text(),'Advice')]/@href", response)
        for url in advice_page_urls:
            print url
            yield Request(url, self.parse_page, response)

    def parse_page(self, response):
        hdoc = HTML(response)
    #   encoded_raw_date = textify(hdoc.select("//ol[@id='threads']/li[last()]/div/div/div/div/div/span/text()")).encode('ISO-8859-1')
    #   unicoded_raw_date = encoded_raw_date.decode('ascii','replace')
    #   decoded_raw_date=unicoded_raw_date.encode('ascii','replace').replace('?',' ')
    #   posted_date = re.findall('.*,[ ](.*)',decoded_raw_date)[0]
    #   posted_dt = parse_date(posted_date)
      
        all_raw_date_time = hdoc.select("//ol[@id='threads']/li | //ol[@id='threads']/li")

        for each in all_raw_date_time:
            raw_date_time = textify(each.select(".//div/dl/dd[2]/text()"))
            posted_dt = parse_date(raw_date_time)
            if posted_dt > self.latest_dt:
                 url = textify(each.select(".//div/div/div/h3/a/@href"))
                 yield Request(url, self.parse_terminal, response)
        next_page_url = textify(hdoc.select("//div[@class='above_threadlist']/div/form/span[@class='prev_next']/a[@rel='next']/@href"))
        yield Request(next_page_url, self.parse_page, response)

def parse_terminal(self, response):
             hdoc = HTML(response)
             author_name = textify(hdoc.select("//ol[@id='posts']/li[1]/div[2]/div/div/div/a/strong/text()"))
             print "\n Author Name : ", author_name

             posted_date = textify(hdoc.select("//ol[@id='posts']/li[1]/div/span/span[@class='date']/text()"))
             posted_time = textify(hdoc.select("//ol[@id='posts']/li[1]/div/span/span[@class='date']/span[@class='time']/text()"))
             print "\n Author Posted Date    : ", posted_date, posted_time
             
             last_user_posted_date = textify(hdoc.select("//ol[@id='posts']/li[last()]/div/span/span[@class='date']/text()"))
             last_user_posted_time = textify(hdoc.select("//ol[@id='posts']/li[last()]/div/span/span[@class='date']/span[@class='time']/text()")) 
             print "\n Last User Posted Date : ", last_user_posted_date, last_user_posted_time


             review_title = textify(hdoc.select("//div[@class='postrow']/h2/text()"))
             print "\n Review Title :", review_title

             author_issue = textify(hdoc.select("//ol[@id='posts']/li[1]/div[2]/div[2]/div/div/div/blockquote/text()"))
             print "\n Review Description : ", author_issue,"\n\n"
