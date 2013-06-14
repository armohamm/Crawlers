from juicer.utils import *
class rob_india(JuicerSpider):
    name = "rob_india"
    start_urls=[]
    for i in range(1,101):
        start_urls.append("http://www.roboticsindia.com/memberlist.php?page=%s&order=asc&sort=username"%(i))
    
    def parse(self, response):
        hdoc = HTML(response)

        nodes = hdoc.select("//td[@class='alt1 username']")
        for node in nodes:
            url = textify(node.select(".//a/@href"))
            yield Request(url, self.parse_terminal, response) 
    def parse_terminal(self, response):
        hdoc = HTML(response)
        name=hdoc.select("//div[@class='blockbody userprof_content userprof_content_border']/h5[@class='subblocksubhead subsubsectionhead first']/text()")
        about_details=hdoc.select("//div[@class='blockbody userprof_content userprof_content_border']/dl")
        stats_section=hdoc.select("//div[@id='view-stats']/div[@class='blockbody subsection userprof_content userprof_content_border']/dl")  
        contact_section=hdoc.select("//div[@id='view-contactinfo']/div[@class='blockbody subsection userprof_content userprof_content_border']/dl")
        print textify(name)
        for each in about_details:
           print textify(each.select(".//dt/text()")), textify(each.select(".//dd/text()"))
        for each in stats_section:
           print textify(each.select(".//dt/text()")), textify(each.select(".//dd/text()"))
        for each in contact_section:
           print textify(each.select(".//dt/text()")), textify(each.select(".//dd/a/text()"))
