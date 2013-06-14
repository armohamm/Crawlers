import re
n=raw_input("enter your choice question")
if n=='1':
   a=raw_input("enter your input")
   res=re.search('.+-([0-9]-[0-9])',a)
   print res.group(1)

elif n=='2':
   a=raw_input("enter your input")
   res=re.search('.*&ptid=([0-9]+)',a)
   print "ptid=",res.group(1)
   res=re.search('.*&pid=([0-9]+)',a)
   print "pid=",res.group(1)
elif n=='3':
   a=raw_input("enter your input")
   res=re.search('.*\?p=([0-9]+)',a)
   print res.group(1)

elif n=='4':
   a=raw_input("enter your input")
   res=re.search('.*,[ ]([0-9][0-9]:[0-9][0-9][ ](PM|AM))',a)
   print res.group(1)

elif n=='5':
   a=raw_input("enter your input")
   res=re.search('(.*),[ ]([0-9][0-9]:[0-9][0-9][ ](PM|AM))',a)
   print res.group(1)

elif n=='6':
   a=raw_input("enter your input")
   res=re.search('.*-([0-9]+-[0-9]).*',a)
   print res.group(1)

elif n=='7':
   a=raw_input("enter your input")
   res=re.search('.*:[ ]([0-9]{2}-[0-9]{2}-[0-9]{4})',a)
   print res.group(1)

elif n=='8':
   a=raw_input("enter your input")
   res=re.search('.*:[ ](.*)',a)
   print res.group(1)
elif n=='9':
   a=raw_input("enter your input")
   res=re.sub('[0-9]{4}',"@",a)
   print res
elif n=='10':
   a=raw_input("enter your input")
   res=re.search('.*\(bot:[ ](.*)\)',a)
   print res.group(1)
elif n=='11':
   a=raw_input("enter your input")
   res=re.match('http://.*?/',a)
   print res.group()
elif n=='12':
   a=raw_input("enter your input")
   res=re.sub('http://.*?/',"http://code.headrun.com/",a)
   print res
elif n=='13':
   a=raw_input("enter your input")
   res=re.match('.*[ ]([0-9]{2}:[0-9]{2}:[0-9]{2})',a)
   print res.group(1)
elif n=='14':
   a=raw_input("enter your input")
   res=re.match('.*([0-9]{2})',a)
   print res.group(1)
elif n=='15':
   print "No question exists!!!"
elif n=='16':
   a=raw_input("enter your input")
   res=re.search('.*([A-Z].[A-Z].[A-Z])',a)
   print res.group(1)
elif n=='17':
   a=raw_input("enter your input")
   res=re.search('.*href="(.*)"',a)
   print res.group(1)
elif n=='18':
   a=raw_input("enter your input")
   res=re.search('{"name":"(.*?)"',a)
   print res.group(1)
elif n=='19':
   a=raw_input("enter your input")
   res=re.search('.*{spider:"(.*)"[ ]}',a)
   print res.group(1)
elif n=='20':
   a=raw_input("enter your input")
   res=re.sub('spider',"hotelpricebot",a)
   print res
else:
   print"Enter Question number between 1 to 20"

