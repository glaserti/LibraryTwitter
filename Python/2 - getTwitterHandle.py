# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Web Scraping for Twitter Handles

# <markdowncell>

# Scraping library homepages for mentioned Twitter handles.
# You need a CSV file with URLs in your current working directory.
# The data structure in the CSV should be a list of dictionaries with keys 'URL', 'Name' [, 'Twitter'].
# (If there is no key 'Twitter' it will be generated. Existing values for this key will be replaced!)
# 
# There will be 3 outputs:
# 
# 1. Prints out a list of tuples for not responding URLs (with Name of Library and URL);
# 1. Prints out a list of dictionaries for libraries without a Twitter handle on their homepage (with Name of Library and URL);
# 1. Exports a CSV file (same name as input file) to cwd (list of dictionaries with additional key 'Twitter' (if not in input file).
# 
# ---
# 
# Data was collected: 2014-02-08

# <headingcell level=2>

# Functions

# <codecell>

import urllib2   # to open a url
import csv
import json

# <codecell>

#import & export CSV

def impCSV(input_file):
    '''
    input_file = csv with keys: "URL", "Twitter"
    output = list of dictionaries
    '''
    f = open(input_file, 'r')
    d = csv.DictReader(f)
    LoD = []   # list of dictionaries
    for row in d:
        LoD.append(row)
    f.close()
    return LoD

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


# <codecell>

def getTwitterHandle(LoD):
    '''
    input = list of dictionaries with keys 'URL' (and 'Twitter')
    output:
    (1) returns = list of dictionaries with keys 'URL' and 'Twitter'
    (2) prints out a list of dictionaries with keys 'Name' and 'URL' 
        for those libraries which don't have a Twitter handle on their homepage
    (3) print out a list of tuples (Name & URL) for not responding URLs
    '''
    UrlError = []
    TwitterLessLibraries = []

    # unifying the URL-structur (in case 'http://' and/or 'www.' are missing)    
    for i in LoD:
        u = i['URL']
        if u[0:7] == 'http://' or u[0:8] == 'https://':
            pass
        else:
            u = u.lstrip('www.')
            u = 'http://www.' + u
            i['URL'] = u
    
    #scraping the homepage of each library for the Twitter handle
    for n in LoD:
        try:
            u = n['URL']
            web = urllib2.urlopen(u)
            webHTML = web.read()
            web.close()
            i0 = webHTML.find('twitter.com')
            i2 = webHTML[i0:].find('"')
            twitter_link = webHTML[i0:i0+i2].rstrip('/"')
            i1 = twitter_link.rfind('/') + 1
            twitter_handle = twitter_link[i1:]
            if i0 == -1:                          # if there is no Twitter handle on the homepage, 
                twitter_handle = '@_@'            # mark missing handle in LoD by '@_@'
                tup = n['Name'], n['URL']         # write Name & URL into a list of tuples
                TwitterLessLibraries.append(tup)
            n['Twitter'] = twitter_handle
        except:                                   # if the URL doesn't answer
            iotup = n['Name'], n['URL']           # write Name & URL into a list of tuples
            UrlError.append(iotup)

    print "URL error occurred with", len(UrlError), "libraries:"
    print json.dumps(UrlError, indent=1)
    print
    print len(TwitterLessLibraries), 'libraries without a Twitter handle on their homepage:'
    print json.dumps(TwitterLessLibraries,indent=1)
    return LoD
      

# <codecell>

def scrapHandles(LoD):
    '''
    LoD = csv file in cwd
    '''
    DictDBS = impCSV(LoD)
    getTwitterHandle(DictDBS)
    exp2CSV(DictDBS, LoD)
    

# <headingcell level=2>

# Function call for each group of libraries

# <codecell>

#[1] for DBS_NatBib.csv
scrapHandles('DBS_NatBib.csv')

# <codecell>

#[2] for DBS_4_UB.csv
scrapHandles('DBS_4_UB.csv')

# <codecell>

#[1] for DBS_1.csv
scrapHandles('DBS_1.csv')

# <codecell>

#[1] for DBS_2.csv
scrapHandles('DBS_2.csv')

# <headingcell level=2>

# Results

# <markdowncell>

# 1. __DBS_NatBib.csv__ 100% success rate: All three libraries have Twitter handles and mention them on their homepage. 
# 1. __DBS_4_UB.csv__ 28 libraries (out of 83) do have a Twitter handle that was accessible from their homepage.
# 
#   To these, following lib accounts have to be added.
#    - _UB Bayreuth_ has a Twitter Account, which was only shortly used in 2010.
#    - _UB Bochum_ and _UB Dortmund_ have Twitter Accounts which are mentioned nowhere on their websites.
#    - _UB Braunschweig_'s homepage returned an (abandoned?) Twitter handle ('frag_die_ubbs') in out commented source code, though their actually used Twitter handle was found on the homepage also ('unibib_bs').
#    - The homepages of _UB Chemnitz_, _UB Ilemnau_, _UB Lüneburg_, _UB Trier_ and _UB Witten Herdecke_ returned only the university's Twitter handle; these were deleted.
#    _SUB Hamburg_ links to their Twitter account, however, this link wasn't found by the Python script due to the html code of the webpage.
#    - The _Zentralbibliothek Sport_ has an non-clickable Twitter icon on their homepage and mentions their Twitter handle sometimes on their (mobile) news pages for new students.
#    - _UB Kaiserslautern_ doesn't have a Twitter account. Some students (?), though, have set up a 'fan account' for their library ('klub386'). This account, however, stopped posting November 2012.
#    - _UB Marburg_ mentions its Twitter account not on the homepage, but on the "news" page ("Aktuelles")
#    - _UB Oldenburg_ only has an abandoned account (last updated 2011) which is not mentioned on their sites.
# 
# 1. __DBS_1.csv__ 6 libraries (out of 18!) do have a Twitter handle.   
#    - _Stadtbibliothek_ Essen had given a landing page as URL to DBS (a "Portalseite"), on their homepage, however, they mentioned their Twitter handle.   
#    - _Stadtbibliothek Köln_ has not mentioned their presence on Twitter on their homepage, but on the page of their "Auskunftsdienst".   
#    - _Stadtbibliothek Bochum_ doesn't have a Twitter account, instead the Twitter handle for Stadt Bochum was returned. This handle was deleted from the list.  
#    - _Hamburger Bücherhallen_ do not have a Twitter account for the entire library system, but for their youth library. This Twitter account was added to the list under the name of the Bücherhallen.
#    
# 1. __DBS_2.csv__ 15 libraries (out of 81!) have a Twitter handle which could be detected on the given (or corrected)<sup>(1)</sup> homepages or via alternate web searches.
# 
#    - _Stadtbibliothek Braunschweig, Darmstadt, Herne, Kiel, Moers, Mühlheim, Osnabrück_ don't have Twitter accounts, instead the Twitter handle for their city were returned. These handles were deleted from the list.
#    - _Stadtbibliothek Erlangen_ had given the URL of the city to DBS. After correcting the URL, the Twitter handle of the library was returned.
#    - _Stadtbibliothek Witten_ had given the URL of the "Kulturforum" to DBS. After correcting the URL, the Twitter handle of the library was returned.
#    
#    - _Stadtbibliothek Freiburg_ did not mention their Twitter account on their websites. Only on the social media information website of the city the handle could be found.
#    - _Stadtbibliothek Salzgitter_ did not mention their Twitter account on their websites. Only on their blog (http://stadtbibliotheksalzgitter.wordpress.com), their Twitter handle was mentioned.
#    - _Stadtbibliothek Solingen_ did not mention their Twitter account. Only on a news page of the city's website, it was mentioned.
#    - _Stadtbibliothek Mannheim_ mentioned only the Twitter handle of the city on their homepage. Their own Twitter account could only be found with a websearch.
#    - _Stadtbibliothek Münster_ does not mention their Twitter account neither on their websites nor on their blog. (This Twitter account is only to inform about problems with library services.)
# 
# 
# ---
# <sup>(1)</sup> For seven libraries, the given URLs had to be corrected (due to misspellings/typos in the DBS or because the URLs were not up do date.

# <headingcell level=2>

# Output of the function calls

# <markdowncell>

# For archival reasons, the output of the function calls is saved here as text:

# <headingcell level=3>

# DBS_NatBib.csv

# <markdowncell>

# URL error occurred with 0 libraries:
# []
# 
# 0 libraries without a Twitter handle on their homepage:
# []

# <headingcell level=3>

# DBS_4_UB.csv

# <markdowncell>

# URL error occurred with 2 libraries:
# [
#  [
#   "Eichst\u00e4tt UB", 
#   "http://www..ku-eichstaett.de/Bibliothek"
#  ], 
#  [
#   "Greifswald UB", 
#   "http://www.uni-greifswald.de/bibliothek/html"
#  ]
# ]
# 
# 56 libraries without a Twitter handle on their homepage:
# [
#  [
#   "Weimar UB", 
#   "http://www.uni-weimar.de/ub"
#  ], 
#  [
#   "Oldenburg UB", 
#   "http://www.bis.uni-oldenburg.de"
#  ], 
#  [
#   "Cottbus TU", 
#   "http://www.tu-cottbus.de/einrichtungen/de/ikmz/servicebereiche/bibliothek.html"
#  ], 
#  [
#   "Frankfurt/O UB", 
#   "http://www.ub.euv-frankfurt-o.de"
#  ], 
#  [
#   "Hagen FernUB", 
#   "http://www.ub.fernuni-hagen.de"
#  ], 
#  [
#   "Berlin UBFU", 
#   "http://www.ub.fu-berlin.de/index.html"
#  ], 
#  [
#   "Vechta HS", 
#   "http://www.uni-vechta.de/einrichtungen/bibliothek"
#  ], 
#  [
#   "Hamburg HCU KrsB", 
#   "http://www.hcu-hamburg.de/imz"
#  ], 
#  [
#   "Stuttgart UB", 
#   "http://www.ub.uni-stuttgart.de/"
#  ], 
#  [
#   "Magdeburg UB", 
#   "http://www.ub.ovgu.de/"
#  ], 
#  [
#   "Aachen BTH", 
#   "http://www.bth.rwth-aachen.de"
#  ], 
#  [
#   "Bochum UB", 
#   "http://www.ub.rub.de"
#  ], 
#  [
#   "Saarbr\u00fccken UuLB", 
#   "http://www.sulb.uni-saarland.de"
#  ], 
#  [
#   "Frankfurt/M SenckB", 
#   "http://www.seb.uni-frankfurt.de/"
#  ], 
#  [
#   "Hamburg SuUB", 
#   "http://www.sub.uni-hamburg.de"
#  ], 
#  [
#   "Freiberg TU Bergakad.", 
#   "http://tu-freiberg.de/ze/ub/"
#  ], 
#  [
#   "M\u00fcnchen UBTU", 
#   "http://www.ub.tum.de"
#  ], 
#  [
#   "Jena UuLB", 
#   "http://www.thulb.uni-jena.de"
#  ], 
#  [
#   "M\u00fcnchen UB BW", 
#   "http://www.unibw.de/unibib/"
#  ], 
#  [
#   "Berlin UdK", 
#   "http://www.udk-berlin.de"
#  ], 
#  [
#   "Konstanz UB", 
#   "http://www.ub.uni-konstanz.de"
#  ], 
#  [
#   "Potsdam UB", 
#   "http://www.ub.uni-potsdam.de"
#  ], 
#  [
#   "Erfurt UFB", 
#   "http://www.uni-erfurt.de/bibliothek/"
#  ], 
#  [
#   "D\u00fcsseldorf UuLB", 
#   "http://www.ub.uni-duesseldorf.de"
#  ], 
#  [
#   "M\u00fcnster UuLB", 
#   "http://www.uni-muenster.de/ULB/"
#  ], 
#  [
#   "Halle/S UuLB", 
#   "http://bibliothek.uni-halle.de"
#  ], 
#  [
#   "K\u00f6ln UuStB", 
#   "http://www.ub.uni-koeln.de"
#  ], 
#  [
#   "Augsburg UB", 
#   "http://www.bibliothek.uni-augsburg.de"
#  ], 
#  [
#   "Bamberg UB", 
#   "http://www.uni-bamberg.de/ub/"
#  ], 
#  [
#   "Bayreuth UB", 
#   "http://www.ub.uni-bayreuth.de/"
#  ], 
#  [
#   "Clausthal-Z. UB", 
#   "http://bibliothek.tu-clausthal.de"
#  ], 
#  [
#   "W\u00fcrzburg UB", 
#   "http://www.bibliothek.uni-wuerzburg.de"
#  ], 
#  [
#   "Dortmund UB", 
#   "http://www.ub.uni-dortmund.de"
#  ], 
#  [
#   "Duisburg-Essen UB", 
#   "http://www.ub.uni-duisburg-essen.de"
#  ], 
#  [
#   "Freiburg/Br UB", 
#   "http://www.ub.uni-freiburg.de"
#  ], 
#  [
#   "Gie\u00dfen UB", 
#   "http://www.ub.uni-giessen.de/"
#  ], 
#  [
#   "Heidelberg UB", 
#   "http://www.ub.uni-heidelberg.de"
#  ], 
#  [
#   "Hildesheim UB", 
#   "http://www.uni-hildesheim.de"
#  ], 
#  [
#   "Frankfurt/M UB", 
#   "http://www.ub.uni-frankfurt.de/"
#  ], 
#  [
#   "Kaiserslautern UB", 
#   "http://www.ub.uni-kl.de/"
#  ], 
#  [
#   "Kiel UB", 
#   "http://www.ub.uni-kiel.de/"
#  ], 
#  [
#   "Koblenz-Landau UB", 
#   "http://www.uni-koblenz-landau.de/bibliothek"
#  ], 
#  [
#   "Mannheim UB", 
#   "http://www.bib.uni-mannheim.de"
#  ], 
#  [
#   "Marburg/L UB", 
#   "http://www.uni-marburg.de/bis/"
#  ], 
#  [
#   "M\u00fcnchen UB", 
#   "http://www.ub.uni-muenchen.de/"
#  ], 
#  [
#   "Osnabr\u00fcck UB", 
#   "http://www.ub.uni-osnabrueck.de"
#  ], 
#  [
#   "Paderborn UB", 
#   "http://www.ub.uni-paderborn.de"
#  ], 
#  [
#   "Passau UB", 
#   "http://www.ub.uni-passau.de/"
#  ], 
#  [
#   "Rostock UB", 
#   "http://www.uni-rostock.de/ub/"
#  ], 
#  [
#   "Siegen UB", 
#   "http://www.ub.uni-siegen.de"
#  ], 
#  [
#   "T\u00fcbingen UB", 
#   "http://www.ub.uni-tuebingen.de"
#  ], 
#  [
#   "Wuppertal UB", 
#   "http://www.bib.uni-wuppertal.de"
#  ], 
#  [
#   "K\u00f6lnSportHS ZB", 
#   "http://www.zbsport.de"
#  ], 
#  [
#   "Flensburg ZHB", 
#   "http://www.zhb-flensburg.de"
#  ], 
#  [
#   "L\u00fcbeck ZHB", 
#   "http://www.zhb.uni-luebeck.de"
#  ], 
#  [
#   "Friedrichshafen Zeppelin UB", 
#   "http://www.zeppelin-university.de/bib"
#  ]
# ]

# <headingcell level=3>

# DBS_1.csv

# <markdowncell>

# URL error occurred with 0 libraries:
# []
# 
# 13 libraries without a Twitter handle on their homepage:
# [
#  [
#   "Leipzig StB", 
#   "http://www.stadtbibliothek.leipzig.de"
#  ], 
#  [
#   "M\u00fcnchen StB", 
#   "http://www.muenchner-stadtbibliothek.de"
#  ], 
#  [
#   "Duisburg StB", 
#   "http://www.stadtbibliothek-duisburg.de"
#  ], 
#  [
#   "Essen StB", 
#   "http://www.stadtbibliothek.essen.de"
#  ], 
#  [
#   "Wuppertal StB", 
#   "http://www.wuppertal.de/stadtbib/"
#  ], 
#  [
#   "Hannover StB", 
#   "http://www.stadtbibliothek-hannover.de"
#  ], 
#  [
#   "N\u00fcrnberg StB", 
#   "http://www.stadtbibliothek.nuernberg.de"
#  ], 
#  [
#   "K\u00f6ln StB", 
#   "http://www.stbib-koeln.de/"
#  ], 
#  [
#   "Stuttgart StB", 
#   "http://www1.stuttgart.de/stadtbibliothek/"
#  ], 
#  [
#   "Frankfurt/M StB", 
#   "http://www.stadtbuecherei.frankfurt.de"
#  ], 
#  [
#   "Dresden StB", 
#   "http://www.bibo-dresden.de"
#  ], 
#  [
#   "Hamburg H\u00d6B", 
#   "http://www.buecherhallen.de"
#  ], 
#  [
#   "Berlin", 
#   "http://www.zlb.de/"
#  ]
# ]

# <headingcell level=3>

# DBS_2.csv

# <markdowncell>

# URL error occurred with 8 libraries:
# [
#  [
#   "Remscheid StB", 
#   "http:// www.remscheid.de/bibliothek"
#  ], 
#  [
#   "G\u00f6ttingen StB", 
#   "http://stadtbibliothekgoettingen.de"
#  ], 
#  [
#   "Ludwigshafen/Rh. StB", 
#   "http://www.ludwigshafen.de/biblioth/home.html"
#  ], 
#  [
#   "Magdeburg StB", 
#   "http://www.stadtbiblothek.magdeburg.de"
#  ], 
#  [
#   "Heidelberg StB", 
#   "http://www.heidelberg.de/stadtbuecherei"
#  ], 
#  [
#   "Recklinghausen StB", 
#   "http://www.recklinghausen.de/Buecherei/Index.html"
#  ], 
#  [
#   "R\u00fcsselsheim StB", 
#   "http://www.stadt.ruesselsheim.de"
#  ], 
#  [
#   "Bergisch Gladbach StB KrsB", 
#   "http://www.stadtbuecherei-gl.de"
#  ]
# ]
# 
# 54 libraries without a Twitter handle on their homepage:
# [
#  [
#   "Dessau StuLB", 
#   "http://www.bibliothek.dessau.de"
#  ], 
#  [
#   "Berlin Pankow StB", 
#   "http://www.berlin.de/ba-pankow/stadtbibliothek/heinrich-boell/"
#  ], 
#  [
#   "L\u00fcbeck StB", 
#   "http://www.stadtbibliothek.luebeck.de"
#  ], 
#  [
#   "Berlin Spandau StB", 
#   "http://www.stadtbibliothek-spandau.de"
#  ], 
#  [
#   "Witten StB", 
#   "http://www.kulturforum-witten.de"
#  ], 
#  [
#   "Leverkusen StB", 
#   "http://www.stadtbibliothek-leverkusen.de"
#  ], 
#  [
#   "Bottrop StB", 
#   "http://www.lebendige-bibliothek.de"
#  ], 
#  [
#   "Mainz StB", 
#   "http://www.mainz.de/WGAPublisher/online/html/default/mkuz-5uzjgd.de.html"
#  ], 
#  [
#   "Potsdam StuLB", 
#   "http://www.bibliothek.potsdam.de"
#  ], 
#  [
#   "Erfurt StuRegB", 
#   "http://bibliothek.erfurt.de"
#  ], 
#  [
#   "Cottbus StuRegB", 
#   "http://www.bibliothek-cottbus.de"
#  ], 
#  [
#   "Bonn StB", 
#   "http://www.bonn.de/stadtbibliothek/"
#  ], 
#  [
#   "Bremerhaven StB", 
#   "http://www.stadtbibliothek-bremerhaven.de"
#  ], 
#  [
#   "Freiburg/Br StB", 
#   "http://www.freiburg.de/stadtbibliothek"
#  ], 
#  [
#   "Heilbronn StB", 
#   "http://www.stadtbibliothek-heilbronn.de"
#  ], 
#  [
#   "Hildesheim StB", 
#   "http://www.stadtbibliothek-hildesheim.de"
#  ], 
#  [
#   "Ludwigsburg StB", 
#   "http://www.stabi-ludwigsburg.de"
#  ], 
#  [
#   "Oldenburg StB", 
#   "http://www.stadtbibliothek-oldenburg.de"
#  ], 
#  [
#   "Paderborn StB", 
#   "http://www.stadtbibliothek-paderborn.de"
#  ], 
#  [
#   "Reutlingen StB", 
#   "http://www.stadtbibliothek-reutlingen.de"
#  ], 
#  [
#   "Rostock StB", 
#   "http://www.rostock.de/stadtbibliothek"
#  ], 
#  [
#   "Salzgitter StB", 
#   "http://www.salzgitter.de/rathaus/fachdienstuebersicht/stadtbibliothek/index.php "
#  ], 
#  [
#   "Schwerin StB", 
#   "http://www.stadtbibliothek-schwerin.de"
#  ], 
#  [
#   "Solingen StB", 
#   "http://www.stadtbibliothek.solingen.de"
#  ], 
#  [
#   "Ulm/Do StB", 
#   "http://www.stadtbibliothek.ulm.de"
#  ], 
#  [
#   "Aachen \u00d6B", 
#   "http://oeffentliche-bibliothek.aachen.de"
#  ], 
#  [
#   "Berlin Lichtenberg StB", 
#   "http://www.stadtbibliothek-berlin-lichtenberg.de"
#  ], 
#  [
#   "Berlin Charlottenburg-W. StB", 
#   "http://www.berlin.de/ba-charlottenburg-wilmersdorf/org/bibliotheken/index.html"
#  ], 
#  [
#   "Berlin Friedrichsh.-Kreuzb.StB", 
#   "http://www.citybibliothek.berlin.de"
#  ], 
#  [
#   "Gelsenkirchen StB", 
#   "http://www.stadtbibliothek-ge.de/"
#  ], 
#  [
#   "Karlsruhe StB", 
#   "http://www.stadtbibliothek-karlsruhe.de"
#  ], 
#  [
#   "Kassel StB", 
#   "http://www.stadtbibliothek-kassel.de"
#  ], 
#  [
#   "Koblenz StB", 
#   "http://www.stb.koblenz.de"
#  ], 
#  [
#   "Mannheim StB", 
#   "http://www.stadtbibliothek.mannheim.de"
#  ], 
#  [
#   "Berlin Mitte StB", 
#   "http://www.citybibliothek.berlin.de"
#  ], 
#  [
#   "Berlin Neuk\u00f6lln StB", 
#   "http://www.stadtbibliothek-neukoelln.de"
#  ], 
#  [
#   "Offenbach/M StB", 
#   "http://www.offenbach.de/stadtbibliothek"
#  ], 
#  [
#   "Berlin Reinickendorf StB", 
#   "http://www.stadtbibliothek-reinickendorf.de"
#  ], 
#  [
#   "Berlin Steglitz StB", 
#   "http://www.stadtbibliothek-steglitz-zehlendorf.de"
#  ], 
#  [
#   "Berlin Tempelhof-Sch\u00f6nebg. StB", 
#   "http://www.stb-tempelhof-schoeneberg.de"
#  ], 
#  [
#   "Berlin Treptow-K\u00f6penick StB", 
#   "http://www.sb-tk.de"
#  ], 
#  [
#   "Wilhelmshaven StB", 
#   "http://www.stadtbibliothek-wilhelmshaven.de"
#  ], 
#  [
#   "Zwickau StB", 
#   "http://www.bibliothek.zwickau.de"
#  ], 
#  [
#   "Wolfsburg StB", 
#   "http://www.stadtbibliothek.wolfsburg.de/"
#  ], 
#  [
#   "Oberhausen StB", 
#   "http://www.bibliothek.oberhausen.de"
#  ], 
#  [
#   "Augsburg StB", 
#   "http://www.stadtbuecherei.augsburg.de"
#  ], 
#  [
#   "Ingolstadt StB", 
#   "http://www.ingolstadt.de/stadtbuecherei"
#  ], 
#  [
#   "L\u00fcdenscheid StB", 
#   "http://www.stadtbuecherei-luedenscheid.de"
#  ], 
#  [
#   "M\u00fcnster StB", 
#   "http://www.muenster.de/stadt/buecherei"
#  ], 
#  [
#   "Regensburg StB", 
#   "http://www.regensburg.de/stadtbuecherei"
#  ], 
#  [
#   "W\u00fcrzburg StB", 
#   "http://www.stadtbuecherei-wuerzburg.de"
#  ], 
#  [
#   "Hagen StB", 
#   "http://www.hagen-medien.de"
#  ], 
#  [
#   "Hamm StB", 
#   "http://www.hamm.de/stadtbuecherei/"
#  ], 
#  [
#   "F\u00fcrth StB", 
#   "http://www.vobue-fuerth.de"
#  ]
# ]

# <codecell>


