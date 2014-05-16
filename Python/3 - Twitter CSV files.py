# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Creating the Twitter CSV files

# <markdowncell>

# Write new csv files with all the libraries with Twitter handles
# 
# - 1 file for the National libraries (3 libraries)
# - 1 file for university libraries (27 libraries)
# - 1 file for public libraries (21 libraries)

# <headingcell level=2>

# Functions

# <codecell>

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


# extracting the tweeting libraries form the files

def twiLibCSV(listname, newFilename):
    '''
    input: the name of the list and a Filename
    output: saves a new LoD with only the tweeting libraries 
            and prints out a status update
    '''
    LoD_2 = []
    for i in listname:
        LoD = impCSV(i)
        for i in LoD:
            if i['Twitter'] != '@_@':
                i['Twitter'] = i['Twitter'].lower()  # the Twitter names given on the websites 
                LoD_2.append(i)                      # and the screen_names in the Twitter accounts 
                                                     # vary sometimes regarding to upper- and lower case!
    exp2CSV(LoD_2, newFilename)
    print 'The new csv file was saved as', newFilename, 'to your current working directory!'
    print
    print 'In this file are', len(LoD_2), 'libraries:'
    print
    print json.dumps(LoD_2, indent=1)
    #return LoD_2

# <headingcell level=2>

# Function calls for the three groups

# <codecell>

uniLib = ['DBS_4_UB.csv']
natLiB = ['DBS_NatBib.csv']
pubLib = ['DBS_1.csv', 'DBS_2.csv']

# <codecell>

twiLibCSV(natLiB, 'NatBibTwitter.csv')

# <codecell>

twiLibCSV(uniLib, 'UniBibTwitter.csv')

# <codecell>

twiLibCSV(pubLib, 'OeBibTwitter.csv')

# <codecell>


