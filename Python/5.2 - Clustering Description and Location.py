# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# In this Notebook, the data collected in the previous Notebook will be cleansed and clustered.
# 
# The description of each account will be clustered to one of the following categories:
# 
#    - Librarian
#    - Library
#    - Publisher
#    - Varia
#    - without a given description
#   
# The location of each account will be clustered to one of the following categories:
# 
#    - local (if the location is the same as the one of the library)
#    - without a given location (" -- ")
#    - otherwise the given location is kept (slightly cleansed)
#    
# The `clustering`-function sums up all the other functions in this Notebook. It takes as input the basicStats-Files and the Friends- and Followers-Files and saves the cleansed and clustered information in the same Friends- and Followers-files. Furthermore the function returns a short report with the clustering and the 15 most mentioned locations.

# <headingcell level=3>

# Helper Functions

# <codecell>

import csv

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

# helper function Prettyprint from MTSW 2 Ed.
from prettytable import PrettyTable   #for pretty printing in a table

def prettyPrint(Sp_1, Sp_2, counted_list_of_tuples):
    ptLang = PrettyTable(field_names=[Sp_1, Sp_2])
    [ptLang.add_row(kv) for kv in counted_list_of_tuples]
    ptLang.align[Sp_1], ptLang.align[Sp_2] = 'l', 'r'
    print ptLang

# <headingcell level=2>

# Description Clustering Functions

# <codecell>

#normalizing the description
def normalizeDescription(LoD):
    normalizeList = LoD
    
    if 'followers_description' in LoD[0].keys():
        for e in range(len(LoD)):
            LoD[e]['followers_description'] = LoD[e]['followers_description'].lower()
    elif 'friends_description' in LoD[0].keys():
        for e in range(len(LoD)):
            LoD[e]['friends_description'] = LoD[e]['friends_description'].lower()
    else:
        pass
    return LoD


def clusterDescription(LoD):
    '''
    input: list of dictionaries
    output: list of dictionaries with clustered and normalized description
    prints out a short status report on the number of items in each cluster
    '''    
    #clustering the list of friends/followers in groups:
    #(1) without description, (2) librarians, (3) libraries, archives, museums, (4) publishers, bookseller etc., (5) varia
    #each id shall only be sorted in one cluster (in the given order)
    #this clustering is "dirty"! E.g. a "book addict"/"buchfanatiker" will be sorted into the publisher bin!
    
    LoD = normalizeDescription(LoD)    
    clusteredLoD = []
    
    if 'followers_description' in LoD[0].keys():
        descrip = 'followers_description'
        user_id = 'followers_user_id'
    elif 'friends_description' in LoD[0].keys():
        descrip = 'friends_description'
        user_id = 'friends_user_id'
        
    librarianKeywords = ['bibliothekar', 'librarian', 'fachrefer', 'malis']
    bibKeywords = ['ub', 'bib', 'librar', 'ULB', 'cherei', 'stabi', 'archiv', 'museum', 'vifa', 'webis']
    bookKeywords = ['buch', 'verleg', 'verlag', 'book', 'publish', 'medien', 'media', 
                    'autor', 'author', 'redaktion', 'zeitung', 'press']
    
    cluster = {}
    cluster['no_Description'] = []
    cluster['Bib'] = []
    cluster['librarian'] = []
    cluster['publisher'] = []
    cluster['varia'] = []
        
    # 1. sorting out the no-description accounts
    copylist = []
    for e in range(len(LoD)):
        if LoD[e][descrip] == "":
            d = LoD[e]
            d['cluster'] = "--"
            clusteredLoD.append(d)           
            cluster['no_Description'].append(LoD[e][user_id])
        else:
            copylist.append(LoD[e])
    
    #2. clustering librarians
    LoD = copylist[:]
    copylist = []
    for e in range(len(LoD)):
        for i in librarianKeywords:
            if i in LoD[e][descrip]:
                d = LoD[e]
                d['cluster'] = "librarian"
                clusteredLoD.append(d)
                cluster['librarian'].append(LoD[e][user_id])
                break
        if LoD[e][user_id] not in cluster['librarian']:
            copylist.append(LoD[e])
    
    #3. clustering libraries
    LoD = copylist[:]
    copylist = []
    for e in range(len(LoD)):
        for i in bibKeywords:
            if i in LoD[e][descrip]:
                d = LoD[e]
                d['cluster'] = "Bib"
                clusteredLoD.append(d)
                cluster['Bib'].append(LoD[e][user_id])
                break
        if LoD[e][user_id] not in cluster['Bib']:
            copylist.append(LoD[e])
    
    #4. clustering book industry
    LoD = copylist[:]
    copylist = []
    for e in range(len(LoD)):
        for i in bookKeywords:
            if i in LoD[e][descrip]:
                d = LoD[e]
                d['cluster'] = "publisher"
                clusteredLoD.append(d)
                cluster['publisher'].append(LoD[e][user_id])
                break
        if LoD[e][user_id] not in cluster['publisher']:
            copylist.append(LoD[e])
    
            
    #5. clustering the varia        
    LoD = copylist[:]
    copylist = []
    for e in range(len(LoD)):
        d = LoD[e]
        d['cluster'] = "varia"
        clusteredLoD.append(d)
        cluster['varia'].append((LoD[e][user_id]))


    #Printing a short report
    print "List length =",len(clusteredLoD)
    print 

    print 'Librarians', len(cluster['librarian'])
    print 'Libraries',len(cluster['Bib'])
    print 'Publisher', len(cluster['publisher'])
    print 'Varia', len(cluster['varia'])
    print 'without Description', len(cluster['no_Description'])
    
    return clusteredLoD


# <headingcell level=2>

# Location Clustering Functions

# <codecell>


def locatingFnFs(LoD):
    '''
    input: list of dictionaries
    output: the LoD with marked empty locations & cleaned up locations
    '''
    
    # getting a counted list of the followers locations 
    
    if 'followers_location' in LoD[0].keys():
        location = 'followers_location'
    elif 'friends_location' in LoD[0].keys():
        location = 'friends_location'
        

    for e in range(len(LoD)):
        if len(LoD[e][location]) < 3:   #marking the locationless accounts
            LoD[e][location] = "--"
        else:
            LoD[e][location] = cleaningLocation(LoD[e][location])
    return LoD

def cleaningLocation(location):
    '''
    input: the location of the twitter account
    output: a normalized str of the location
    '''
    import re
    # list of words to remove from the location's description (Bundesländer & Country)
    removeWords = ['deutschland', 'germany', 'baden-württemberg', 'bayern', 'brandenburg', 'hessen', 'Mecklenburg-Vorpommern', 
              'niedersachsen', 'nordrhein-Westfalen', 'rheinland-Pfalz', 'saarland', 'sachsen', 
              'sachsen-anhalt', 'schleswig-holstein','thüringen', 'europa', 'europe'] #ausser 'Berlin', 'Bremen', 'Hamburg'!

    # normalizing English => German names:
    eng = [('munich', 'münchen'), ('muenchen', 'münchen'), ('cologne', 'köln'), ('nuremberg', 'nürnberg'), 
           ('frankfurt', 'frankfurt'), ('vienna', 'wien')]
    
    #normalizing location (lowercase, stripping of Germany etc.) ("Oldenburg, Germany", "Hessen, Kassel"))
    location = location.lower()
    for e in eng:
        if e[0] in location:
            location = e[1]
            break
    location = re.sub('[/,]', ' ', location)  #remove separator
    for w in removeWords:   #remove Bundesland and/or Country
        if w in location:
            location = location.replace(w,'')
            location = location.strip()   #strip off white space
            if len(location) == 0:
                location = '--'
    return location


def ReportLocatingFnFs(LoD):
    '''
    input: list of dictionaries
    output: a counted list of tuples of the 15 most mentioned locations
    '''
    from collections import Counter       #for turning lists to dictionaries etc.
    
    # getting a counted list of the followers locations 
    locList = []

    if 'followers_location' in LoD[0].keys():
        location = 'followers_location'
    elif 'friends_location' in LoD[0].keys():
        location = 'friends_location'
    
    for e in range(len(LoD)):
        locList.append(LoD[e][location])    
        
    countedLocations = Counter(locList) #type = class: Counter({u'Uni_MR': 12, u'glaserti': 10, ...})
    allLocations = countedLocations.most_common(15)
    return allLocations

#
# This function wraps up all the other functions in this Notebook
#

def clustering(basicStatsFile,timeStamp):
    '''
    input: filename of 'NatBib_BasicStats_2014-04-06.csv', etc. and
    Timestamp = Timestamp of the friends/followers files
    output: updates the friends/followers files and prints out an error message if no 
    such file could be accessed
    '''

    LoT = []
    errorList = []
    
    f = impCSV(basicStatsFile)

    # create a tuple for each entry in the list with twitter handle and place
    for e in f:
        t = (e['screen_name'], e['location'])
        LoT.append(t)
    
    # for each tuple[0] open the corresponding Libname__Friends_Timestamp.csv and _Follower_Timestamp.csv
    for e in LoT:
        f1 = ''
        f2 = ''
        filename1 = e[0] + '_Friends_' + timeStamp + '.csv'
        filename2 = e[0] + '_Followers_' + timeStamp + '.csv'
        
        # only open if such a file exists - otherwise create an error list
        try:
            f1 = impCSV(filename1)
        except:
            errorList.append(filename1)
        try:
            f2 = impCSV(filename2)
        except:
            errorList.append(filename2)  

        libLocation = e[1]                     # get the location of the library
        
        if f1 != '':
            print 
            print len(filename1)*'='
            print filename1
            print len(filename1)*'='
            print
            f1 = clusterDescription(f1)
            f1 = locatingFnFs(f1)

            # if friends_location is identical with libLocation, replace location with 'local'
            for e in range(len(f1)):
                if libLocation in f1[e]['friends_location']:
                    f1[e]['friends_location'] = 'local'
            rep = ReportLocatingFnFs(f1)
            print
            prettyPrint('Location', 'Count', rep)
            print 
        if f2 != '':
            print
            print len(filename2)*'='
            print filename2
            print len(filename2)*'='
            print
            f2 = clusterDescription(f2)
            f2 = locatingFnFs(f2)
            for e in range(len(f2)):
                if libLocation in f2[e]['followers_location']:
                    f2[e]['followers_location'] = 'local'
                    f2[e]['followers_location'] = 'local'
            rep = ReportLocatingFnFs(f2)
            print
            prettyPrint('Location', 'Count', rep)
            print 
         
        # save files
        if f1 != '':
            exp2CSV(f1,filename1)
        if f2 != '':
            exp2CSV(f2,filename2)
        
    #print an error message
    if len(errorList) > 0:
        print 'These files could not be accessed:', errorList

# <headingcell level=3>

# Supplementary Functions

# <codecell>

#printing out the description for the 'Varia' for further investigation

def printClusterReport(LoD):
    import json
    for e in range(len(LoD)):
        if LoD[e]['cluster'] == 'varia':
            if 'friends_description' in LoD[e]:
                print json.dumps(LoD[e]['friends_description'], indent = 1)
            else:
                print json.dumps(LoD[e]['followers_description'], indent = 1)

# <headingcell level=2>

# Function Calls

# <codecell>

clustering('NatBib_BasicStats_2014-04-06.csv', '2014-04-07')

# <codecell>

clustering('UniBib_BasicStats_2014-04-06.csv', '2014-04-06')

# <codecell>

clustering('OeBib_BasicStats_2014-04-06.csv', '2014-04-06')

# <codecell>


