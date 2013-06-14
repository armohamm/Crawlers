from juicer.utils import *

class Flip_Mobile(JuicerSpider):
    name = "flip_mobile"
    start_urls = "http://www.flipkart.com/mobiles?otracker=hp_main_mobiles_title"

    def parse(self, response):
        hdoc = HTML(response)

        nodes = hdoc.select("//div[@class='grid-row line']//div[contains(@class,'size1of4 fk-medium-atom')]")
        for node in nodes:
        #    print '{0:80} ==> {1:10}==> {2:10}'.format(textify(node.select(".//a/text()")),textify(node.select(".//div[@class='fk-stars-small']/@title")),textify(node.select(".//span[contains(@class,'price final-price')]/text()")))
            url = textify(node.select(".//a/@href"))
            yield Request(url, self.parse_terminal, response) 


    def parse_terminal(self, response):
        hdoc = HTML(response)
        spec_nodes=hdoc.select("//div[contains(@class,'item_desc_text')]//ul[@class='fk-key-features']//li | //div[@class='item_desc_text line']//ul[@class='feature_bullet']//li//span")
        mob_name=hdoc.select("//div[@class='mprod-summary-title fksk-mprod-summary-title']/h1/text()")
        rating = hdoc.select("//div[@class='mprod-summary-title fksk-mprod-summary-title']//div[@class='fk-stars']/@title")
        price=hdoc.select("//div[@class='shop-section line bmargin10 tmargin5']//div[@class='prices']/span/text()")
        
        no_of_ratings=hdoc.select("//div[@class='mprod-summary-title fksk-mprod-summary-title']//span[@itemprop='ratingCount']/text()")
        review_title=hdoc.select("//div[@class='lastUnit size4of5 section2']/div[@class='line fk-font-big bmargin5']/strong/text()")
        reviews_comments=hdoc.select("//div[@class='lastUnit size4of5 section2']//p[@class='line bmargin10']")
        print "\n"
        "Name: %s"%(textify(mob_name))
        print "Rating:", textify(rating)
        print "Price:", textify(price)
        print "No of Ratings:",textify(no_of_ratings)
        print "Key Specifications:-:-:"
        for node in spec_nodes:
            print '{0:20} {1:50}'.format(" ",textify(node.select(".//text()")))
        print "Review Title:", textify(review_title)
        for comment in reviews_comments:
             print "Review Comments:"
             print  textify(comment.select(".//text()")), "\n\n"
