#
# Scraping website for information about libraries
#

# For getting information about the libraries, the database of the German Library Statistics (Deutsche Bibliotheksstatistik/DBS) which is hosted by the HBZ was used:
# 
# http://www.bibliotheksstatistik.de/eingabe/dynrep/adrbrowser/bibs.php
# 
# For this project, 4 different requests were made:
# 
# 1. DBS National Libraries   ( == > 3 active<sup>(1)</sup> libraries)
# 1. DBS Section 4: University Libraries (i.e. not the entire Section 4 was queried) ( == > 83 active<sup>(2)</sup> libraries)
# 1. DBS Section 1: Public Libraries with population > 400,000 ( == > 18 libraries)<sup>(3)</sup>
# 1. DBS Section 2: Public Libraries with population > 100,000 ( == > 81 libraries)<sup>(4)</sup>
# 
# Since the website doesn't give unique URLs for individual requests, 
# you could download the source code of each database request and safe as html files.
# 
# However, you could use the _printing page_ of the database result list, which returns
# an individual URL. This procedure is followed here, with the URLs given in the list of tuples "urlList".
# 
# The result will be saved as a csv file for each database request to the cwd (i.e. current working directory).<sup>(5)</sup>
# Furthermore, those libraries without a valid url will be printed out (in a JSON prettyprint style).
# 
# ---
# 
# <sup>(1)</sup> In DBS National Libraries, there are actually four libraries listed, but one is inactive.
# 
# <sup>(2)</sup> In DBS Section 4: University Libraries, there are actually 84 libraries listed, but one is inactive.
# 
# <sup>(3)</sup> Two libraries were added manually to this goup of libraries: The Hamburger Bücherhallen, whose  entry in DBS omitted the DBV Section, and the Zentral- und Landesbibliothek Berlin, which was listed as member of Section 4 "Wissenschaftliche Universalbibliotheken", though the library is member of Section 1 (and only guest member of Section 4 according to the DBV webpage (http://www.bibliotheksverband.de/mitglieder/).
# 
# <sup>(4)</sup> From DBS Section 2, two libraries (KA119 and KA129) were removed: These are small "ehrenamtlich geführte" libraries (less than 1,000 books) without any presence on the internet.
# For two more libraries (MB026 and GY440) the urls, missing in the DBS, were added manually.
# 
# <sup>(5)</sup> To find out, what your cwd is, type:
# 
# >```import os
# >print os.getcwd()```
# 
# ---
# 
# Data was collected: 2014-02-08


#
# List of URLs
#

# List of tuples of name & url
# urlList[0] = Nr. 1 (DBS National Libraries)
# urlList[1] = Nr. 2 (DBS Section 4, University Libraries)
# urlList[2] = Nr. 3 (DBS Section 1)
# urlList[3] = Nr. 4 (DBS Section 2)


urlList = [('DBS_NatBib', 'http://www.bibliotheksstatistik.de/eingabe/dynrep/adrbrowser/adrbrowser.php?prt=AG012|AG292|AG000|AK001'),
           ('DBS_4_UB', 'http://www.bibliotheksstatistik.de/eingabe/dynrep/adrbrowser/adrbrowser.php?prt=EM482|AH715|EJ882|EX035|AA708|AG188|DB900|DE081|AD011|DB079|AF093|AH090|AA289|MM201|AF007|EL283|AJ082|AB294|AD291|AE088|AX001|AA046|AC018|AB105|AA083|EL131|AE830|AL091|AE027|BK213|AX566|AL352|AK517|EX461|AL005|AL017|AG061|AC006|AE003|AB038|AK384|AD473|AH703|AB361|AD084|AK104|AF020|AA290|DE100|SB005|AL029|AK025|AB026|AA009|AH089|AH016|AN087|AJ100|EL039|AC030|AE386|AA034|AJ008|BD987|AE015|BD296|AH077|AE180|AH004|AF019|AK700|AH466|AH739|AJ355|AH028|AL467|AB385|AJ021|BZ398|AC468|DC072|DA385|BE926|FH880'),
           ('DBS_1', 'http://www.bibliotheksstatistik.de/eingabe/dynrep/adrbrowser/adrbrowser.php?prt=AJ197|GE486|AA381|AE131|AH478|AJ136|AE064|AK062|AG115|AB075|AJ380|AL480|AH132|AA277|AE362|AE106'),
           ('DBS_2', 'http://www.bibliotheksstatistik.de/eingabe/dynrep/adrbrowser/adrbrowser.php?prt=AF111|MB026|GB291|AH259|GC556|KA119|KA129|GD895|AJ367|AF238|AD242|AD072|AG243|GY440|AA186|AB063|AH181|AD369|AC134|AF135|GE231|KS124|AL285|AF196|KQ152|AK116|AG279|AE295|AD217|GD822|AK153|GM675|AG267|AK293|AC286|AB178|AF275|AJ033|AL157|AC122|AJ471|WB861|LD510|GC283|AD059|MB038|AA174|AG371|AG231|LC499|LC505|AJ069|AG073|GB850|WB782|MB014|AH260|AH168|GC301|AJ264|GD998|GE012|GE036|MB002|GD767|AD163|AH351|AC262|GA444|GE462|GB746|AA472|GE899|AH247|AA447|AB270|GE164|GA596|AH284|AF470|AB142|AD229|JA868')]


#
# Functions
#

from bs4 import BeautifulSoup
import urllib2
import json
import csv


def writeDict(bsString):
    
    s = bsString.lstrip()   # stripping off leading whitespace
    i1 = s.find("(DBS-ID: ")
    i2 = i1 + len("(DBS-ID: ")
    i3 = s.find(", Sig.")   # if there is no Sig. given, i3 returns -1 [i.e. the closing paren ")"]
    name = s[:i1-1]
    i4 = name.find(' ')   # to get the place, split name at first white space
    dbsID = s[i2:i3]
    place = name[:i4]
    dic = {}
    dic['DBS-ID'] = dbsID.encode("utf-8")   # BeautifulSoup encodes in Unicode,
    dic['Name'] = name.encode("utf-8")      # which is not supported by csv;
    dic['Ort'] = place.encode("utf-8")      # hence encoding to utf-8 is necessary
    dic['Twitter'] = ''
    return dic

def findURL(soupTAG):
    urlTAG = soupTAG.find_next("a")
    url = urlTAG.get('href')
    d = {}
    d['URL'] = url.encode("utf-8")
    return d

def parseHTML(soupHTML):
    
    l = []
    loD = []
    s0 = soupHTML.table.table.h3
    while type(s0) != type(None):    # first write each entry which is not NoneType to a list
        l.append(s0)
        s_next = s0.find_next("h3")
        s0 = s_next
        
    for i in l:                           
        url = findURL(i)             # finding the next url for each entry        
        si = i.string                # second write each string of the list which is not NoneType  
        if type(si) != type(None):   # to a List of Dictionaries
            di = writeDict(si)
            di.update(url)           # adding the url to the dict
            loD.append(di)
        else:
            pass
    return loD


def libCSV(index_of_urlList):
    '''
    pass as argument the index number of the urlList
    prints out 
    (1.) Nr. of (active) libraries in the list
    (2.) A JSON prettyprint list of libraries without a valid url
    (3.) The name of the csv file.
    Saves the csv file in the cwd.
    
    '''
    tup = urlList[index_of_urlList]
    u = tup[1]
    web = urllib2.urlopen(u)
    webHTML = web.read()
    web.close()
    soup = BeautifulSoup(webHTML)
    
    result = parseHTML(soup)
    print 'For', tup[0], len(result), '(active) libraries could be found.'
    for i in result:
        if i["URL"] == "":
            print 'For this library no URL could be found: \n'
            print json.dumps(i, indent=1), '\n'
            
    filename = tup[0] + '.csv'
    l1 = len(filename) + len('The csv will be safed as ')
    print "\n"+ l1*"=" + "\n"
    print 'The csv will be safed as', filename
    return exp2CSV(result, filename)


def exp2CSV(listOfDict, filename):
    '''
    arguments = list of dictionaries, filename
    output = saves file to cwd (current working directory)
    '''
    outputfile = filename
    keyz = listOfDict[0].keys()
    f = open(outputfile,'w')
    dict_writer = csv.DictWriter(f,keyz)
    dict_writer.writer.writerow(keyz)
    dict_writer.writerows(listOfDict)
    f.close()


