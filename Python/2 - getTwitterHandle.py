#
# Web Scraping for Twitter Handles
#


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


#
# Functions
#

import urllib2   # to open a url
import csv
import json

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
      


def scrapHandles(LoD):
    '''
    LoD = csv file in cwd
    '''
    DictDBS = impCSV(LoD)
    getTwitterHandle(DictDBS)
    exp2CSV(DictDBS, LoD)
    
