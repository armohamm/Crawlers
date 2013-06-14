from juicer.utils import *
class hadoop_users(JuicerSpider):
      name = "hadoop_users"
      start_urls="http://wiki.apache.org/hadoop/PoweredBy"
      def parse(self, response):
         hdoc = HTML(response)
         nodes = hdoc.select("//a[@class='http']") 
         #f=open("hadoop_users",'a')
         for each in nodes:
           print textify(each.select("./text()")),textify(each.select("./@href"))
           #textify(each.select("./text()")).encode('ascii','replace')
             #encode can be used to  convert unicode to ascii but should be in range 1 to 128 if not we use 'replace'
           #textify(each.select("./@href")).encode('ascii','replace')
