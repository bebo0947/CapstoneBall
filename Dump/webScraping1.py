from bs4 import BeautifulSoup as bs
import urllib.request

fb = urllib.request.urlopen("https://fbref.com/en/comps/Big5/2017-2018/stats/players/2017-2018-Big-5-European-Leagues-Stats")
mb = fb.read()
mystr = mb.decode('utf8')
fb.close()

print(mystr)

with open('https://fbref.com/en/comps/Big5/2017-2018/stats/players/2017-2018-Big-5-European-Leagues-Stats', 'r') as web:
    content = web.read()
    print(content)



