from bs4 import BeautifulSoup
import traceback,sys

fr = open("../data/company_code.htm", 'r')
text = fr.read()
fr.close()
soup = BeautifulSoup(text)

fw = open("../data/company_codes.txt", 'w')
data = soup.findAll('div',attrs={'class': 'row'})
for i in data:
    #print i
    #print type(i.contents)
    isoup = BeautifulSoup(str(i.contents))
    idata = isoup.findAll('li')
    company = ""
    bse = ""
    nse = ""
    for jid,j in enumerate(idata):
        try:
            if jid == 0: company = ''.join(j.findAll(text=True))
            elif jid == 1: bse = ''.join(j.findAll(text=True))
            elif jid == 2: nse = ''.join(j.findAll(text=True))
        except:
            print i
            traceback.print_exc()
            sys.exit(0)
    print company+"\t"+bse+"\t"+nse
    fw.write(company+"\t"+bse+"\t"+nse+"\n")
fw.close()