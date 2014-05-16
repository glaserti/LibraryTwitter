# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Basic Statistics on the Twitter Accounts

# <markdowncell>

# In this section, some basic statistics for the Twitter Accounts of the given groups of libraries (i.e. National libraries, University libraries, Public libraries) will be collected.
# 
# The functions will return a list of dictionaries and save it as a CSV to the cwd.
# 
# The dictionaries have as keys: 
# 
# - 'created_at' ( = the Twitter Time Stamp),
# - 'created_at_sec' ( = the date in seconds (from 1970-01-01), 
# - 'days' (= the number of days since created_at), 
# - 'days_since_last_tweet', 
# - 'followers_count', 
# - 'friends_count', 
# - 'id_str' ( = the Twitter ID as a string), 
# - 'location' ( = if a location is given in the description of the account), 
# - 'screen_name' ( = the Twitter handle/username), 
# - 'statuses_count' ( = Nr. of Tweets), 
# - 'tweets_per_day', 
# - 'tweets_per_year'
# 
# Finally, there is a Report section, in which an overview is provided. For each library group will be printed out:
# 
# - The number of libraries,
# - the median of the groups' Tweets per day,
# - the oldest and latest library @ Twitter with their Tweets per day ratio,
# - a list of no longer actively tweeting libraries
# - the libraries with the most and least Tweets and
# - a summary for each library.
# 

# <headingcell level=2>

# Function definitions

# <codecell>

# authenticating @ Twitter

# Function definition taken from Mining the Social Web, 2. Ed.
# cf. https://github.com/ptwobrussell/Mining-the-Social-Web-2nd-Edition

'''
Go to http://dev.twitter.com/apps/new to create an app and get values
for these credentials, which you'll need to provide in place of these
empty string values that are defined as placeholders.
See https://dev.twitter.com/docs/auth/oauth for more information 
on Twitter's OAuth implementation.
'''
    
#importing libraries
import twitter
    
CONSUMER_KEY = 
CONSUMER_SECRET =
OAUTH_TOKEN = 
OAUTH_TOKEN_SECRET = 

    
auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)
twitter_api = twitter.Twitter(auth=auth)

    

# <codecell>

#import & export CSV
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
    #creating the filename of the csv with current datestamp 
    import datetime
    datestamp = datetime.datetime.now().strftime('%Y-%m-%d')    
    outputfile = filename[:-4]+ '_' + datestamp + '.csv'
    keyz = listOfDict[0].keys()
    f = open(outputfile,'w')
    dict_writer = csv.DictWriter(f,keyz)
    dict_writer.writer.writerow(keyz)
    dict_writer.writerows(listOfDict)
    f.close()

# <codecell>

###################################
#                                 #
#  Functions for the Data Mining  #
#                                 #
###################################


#importing libraries
import json                           #for pretty printing
import time                           #for calculating Tweets per day
import operator                       #for sorting dictionaries
from collections import Counter       #for turning lists to dictionaries etc.
from prettytable import PrettyTable   #for pretty printing in a table


# getting the ListOfScreenNames
def getLoSN(csvFile):
    '''
    input = csv filename of list of dictionaries with a key "Twitter" (where the Screenname is saved)
    returns a list of tuples with t[0] = libLocation, t[1] = Twitter screenname
    '''
    LoD = impCSV(csvFile)
    ListOfScreenNamesLocationTuples = []
    for i in LoD:
        ListOfScreenNamesLocationTuples.append((i['Ort'], i['Twitter']))
    return ListOfScreenNamesLocationTuples



#getting basic infos for a given account incl. last status update
# users.lookup = max. 100 Anfragen pro Session! Not a problem in this section of the queries.
def AccountInfo(L):
    '''
    input = list of tuples with str of screen_names and location
    output = list of tuples with t[0] = libLocation, t[1] = lists of dictionaries
    '''
    outputList = []
    errorList = []   #implementation of error checking via "try" or something like that!
    for n in L:
        search_results = twitter_api.users.lookup(screen_name=n[1])
        outputList.append((n[0], search_results))
    return outputList



# getting some basic stats for the screen_names
def baseStats(AccountInfoList):
    '''
    input = return list from AccountInfo(L)
    output: list of dictionaries with screenName, UserID, nrOfFollowers, nrOfFriends, 
    nrOfStatusUpdates, tweetsSince, tweetsPerDay, and tweetsPerYear
    '''
    AccountInfoList[1]
    baseStatsList = []
    for e in range(len(AccountInfoList)):
        newDict = {}   #creating a new dictionary for each account
        screenName = AccountInfoList[e][1][0]['screen_name'].lower()  # cf. @ Notebook 3 - Twitter CSV files
        UserID = AccountInfoList[e][1][0]['id_str'].encode('utf-8')
        nrOfFollowers = AccountInfoList[e][1][0]['followers_count']   #How many Followers?
        nrOfFriends = AccountInfoList[e][1][0]['friends_count']   #How many Following/Friends?
        nrOfStatusUpdates = AccountInfoList[e][1][0]['statuses_count']
        tweetsSince = AccountInfoList[e][1][0]['created_at'].encode('utf-8')
        #new in Dict:
        DateOfLastTweet = AccountInfoList[e][1][0]['status']['created_at'].encode('utf-8')
        
        #normalizing the location
        
        '''
        # This code is only necessary if the Twitter location is used instead of the DBS location
        # location = AccountInfoList[e][1][0]['location'].encode('utf-8')   #get the location (in case the screen_name isn't sufficient)
        # list of words to remove from the location's description (Bundesländer & Country)
        removeWords = ['Deutschland', 'Germany', 'Baden-Württemberg', 'Bayern', 'Brandenburg', 'Hessen', 'Mecklenburg-Vorpommern', 
              'Niedersachsen', 'Nordrhein-Westfalen', 'Rheinland-Pfalz', 'Saarland', 'Sachsen', 
              'Sachsen-Anhalt', 'Schleswig-Holstein','Thüringen'] #ausser 'Berlin', 'Bremen', 'Hamburg'!

        #normalizing location (lowercase, stripping of Germany etc.) ("Oldenburg, Germany", "Hessen, Kassel"))
        location = (location.replace(",", "")).lower()   #remove separator and normalize to lowercase
        for e in removeWords:   #remove Bundesland and/or Country
            if e.lower() in location:
                location = location.strip(e.lower())
                location = location.strip()   #strip off white space
        '''
        location = AccountInfoList[e][0].lower()
        idxLoc1 = location.find('/')          # strip off everything from '/' on to the right (e.g. 'Frankfurt/M')
        idxLoc2 = location.find('-')          # strip off everything from '-' on to the right (e.g. 'Duisburg-Essen')
        if idxLoc1 != -1:
            location = location[:idxLoc1]
        if idxLoc2 != -1:
            location = location[:idxLoc2]
        if 'sporths' in location:
            location = location.strip('sporths')   # the lib of KölnSportHS has given that as their location!
         
        
        #calculating Tweets per day and year
        t0 = time.mktime(time.strptime(tweetsSince, "%a %b %d %H:%M:%S +0000 %Y"))#returns date in seconds (from 1970-01-01)
        t1 = time.time() #returns current date in seconds (from 1970-01-01)
        diff = int(round((t1 - t0)/86400)) #calculates the difference in days (86400 sec per day)
        tweetsPerDay = round((float(nrOfStatusUpdates)/diff),2)   #returns nr of Tweets per day as a float
        diffYear = round((diff/365.0),2)
        tweetsPerYear = round((float(nrOfStatusUpdates)/diffYear),2)   #returns nr of Tweets per year as a float
        
        #calculating time since last Tweet
        LastTweet_t0 = time.mktime(time.strptime(DateOfLastTweet, "%a %b %d %H:%M:%S +0000 %Y"))
        daysSinceLastTweet = int(round((t1 - LastTweet_t0)/86400))
        
        #writing to the dictionary
        newDict['screen_name'] = screenName
        newDict['id_str'] = UserID
        newDict['location'] = location
        newDict['followers_count'] = nrOfFollowers
        newDict['friends_count'] = nrOfFriends
        newDict['statuses_count'] = nrOfStatusUpdates
        newDict['created_at'] = tweetsSince
        newDict['created_at_sec'] = t0
        newDict['days'] = diff
        newDict['tweets_per_day'] = tweetsPerDay
        newDict['tweets_per_year'] = tweetsPerYear
        newDict['days_since_last_tweet'] = daysSinceLastTweet
        baseStatsList.append(newDict) #writing to the List
        
    return baseStatsList



########################################
#                                      #
#  Function for the reporting section  #
#                                      #
########################################


#return the median of Tweets per Day
def medianOfTPD(LoD):
    l = []
    for e in LoD:
        l.append(e['tweets_per_day'])
    l.sort()
    if len(l)%2 != 0:
        median = l[len(l)/2]
    else:
        median = (l[len(l)/2-1] + l[len(l)/2])/2.0
    return median


#Sorting the Accounts based on created_at
def sortingDate(L):
    '''
    input = baseStats(StatusLists) or list of dicts
    output = sorted list of dicts from oldest to newest account
    '''
    l=L[:]
    l.sort(key=operator.itemgetter('created_at_sec'))
    return l


#Sorting the Accounts based on days_since_last_tweet
def sortingDateOfLastTweet(L):
    '''
    input = baseStats(StatusLists) or list of dicts
    output = sorted list of dicts from oldest to newest account
    '''
    l=L[:]
    l.sort(key=operator.itemgetter('days_since_last_tweet'))
    return l

#get the inactive accounts (i.e. accounts without a Tweet in the last 100 days
def getInactiveAccounts(sortingDateOfLastTweet):
    l = []
    for e in sortingDateOfLastTweet:
        if e['days_since_last_tweet'] > 100:
            l.append(e['screen_name'])
    if len(l) == 0:
        print 'There is no inactive library in this group. (I.e. all libraries have tweeted in the last 100 days.)'
    elif len(l) == 1:
        print l[0], "hasn't tweeted in the last 100 days. This library can be considered inactive on Twitter." 
    else:
        s = ", ".join(l)
        print s, "haven't tweeted in the last 100 days. These libraries can be considered inactive on Twitter." 


        
#Sorting the Accounts based on number of Tweets
def sortingTweets(L):
    '''
    input = baseStatsList(StatusLists) or list of dicts
    output = sorted list of dicts from lousiest Tweeter to SocialMedia Addict
    '''
    li=L[:]
    import operator
    li.sort(key=operator.itemgetter('statuses_count'))
    return li
        
#Printing a summary sorted by date
def printSummary(dictList):
    '''a small function to print a summary of the list of dicts sorted by date'''
    for e in range(len(dictList)):
        print dictList[e]['location'], ':', dictList[e]['screen_name'], '= UserID:', dictList[e]['id_str']
        print '--> Followers:', dictList[e]['followers_count'], '; Following:', dictList[e]['friends_count'], '; Tweets:', dictList[e]['statuses_count']
        print '--> Tweets since:', dictList[e]['created_at'][4:7], dictList[e]['created_at'][-4:], '=', dictList[e]['days'], 'days', '; Tweets per day:', dictList[e]['tweets_per_day']
        print


# <headingcell level=2>

# Requesting Data

# <headingcell level=3>

# 1. National Libraries

# <codecell>

# 1: get the list of screennames
# ==> insert csv-name  !!
NatBib_libList = getLoSN('NatBibTwitter.csv')
print len(NatBib_libList), 'libraries were data mined'

# 2: get the account information for each screenname
NatBib_accountInfoList = AccountInfo(NatBib_libList)

# 3: get some basic stats and write them to a list of dictionaries
NatBib_baseStatsList = baseStats(NatBib_accountInfoList)

# 4: save this LoD as a csv to the cwd
# ==> insert csv-name  !!
exp2CSV(NatBib_baseStatsList, 'NatBib_BasicStats.csv')
print 'The findings were saved as a CSV file to your cwd as NatBib_BasicStats_[current datestamp].csv'

# <headingcell level=3>

# 2. University Libraries

# <codecell>

# 1: get the list of screennames
# ==> insert csv-name  !!
UniBib_libList = getLoSN('UniBibTwitter.csv')
print len(UniBib_libList), 'libraries were data mined'

# 2: get the account information for each screenname
UniBib_accountInfoList = AccountInfo(UniBib_libList)

# 3: get some basic stats and write them to a list of dictionaries
UniBib_baseStatsList = baseStats(UniBib_accountInfoList)

# 4: save this LoD as a csv to the cwd
# ==> insert csv-name  !!
exp2CSV(UniBib_baseStatsList, 'UniBib_BasicStats.csv')
print 'The findings were saved as a CSV file to your cwd as UniBib_BasicStats_[current datestamp].csv.'

# <headingcell level=3>

# 3. Public Libraries

# <codecell>

# 1: get the list of screennames
# ==> insert csv-name  !!
OeBib_libList = getLoSN('OeBibTwitter.csv')
print len(OeBib_libList), 'libraries were queried.'

# 2: get the account information for each screenname
OeBib_accountInfoList = AccountInfo(OeBib_libList)

# 3: get some basic stats and write them to a list of dictionaries
OeBib_baseStatsList = baseStats(OeBib_accountInfoList)

# 4: save this LoD as a csv to the cwd
# ==> insert csv-name  !!
exp2CSV(OeBib_baseStatsList, 'OeBib_BasicStats.csv')
print 'The findings were saved as a CSV file to your cwd as OeBib_BasicStats_[current datestamp].csv.'


# <headingcell level=2>

# Report

# <headingcell level=4>

# National Libraries

# <codecell>

NatBib_median = medianOfTPD(NatBib_baseStatsList)

NatBib_dateSortList = sortingDate(NatBib_baseStatsList)

NatBib_tweetSortList = sortingTweets(NatBib_baseStatsList)

#--------

print 'There are', len(NatBib_libList), 'libraries in this category.'
print
print 'Taken the median, on average these libraries send about', NatBib_median, 'Tweets per day.'
print
print 'Oldest account:', NatBib_dateSortList[0]['screen_name'], 'with', NatBib_dateSortList[0]['tweets_per_day'], 'Tweets per day.' 
print 'Latest account:', NatBib_dateSortList[-1]['screen_name'], 'with', NatBib_dateSortList[-1]['tweets_per_day'], 'Tweets per day.' 
print
getInactiveAccounts(NatBib_baseStatsList)
print
print 'Lousiest Tweeter:', NatBib_tweetSortList[0]['screen_name'], 'with', NatBib_tweetSortList[0]['statuses_count'], 'Tweets.' 
print 'SocialMedia Addict:', NatBib_tweetSortList[-1]['screen_name'], 'with', NatBib_tweetSortList[-1]['statuses_count'], 'Tweets.' 
print
printSummary(NatBib_dateSortList)


# <headingcell level=4>

# University Libraries

# <codecell>

UniBib_median = medianOfTPD(UniBib_baseStatsList)

UniBib_dateSortList = sortingDate(UniBib_baseStatsList)

UniBib_tweetSortList = sortingTweets(UniBib_baseStatsList)


#--------

print 'There are', len(UniBib_libList), 'libraries in this category.'
print
print 'Taken the median, on average these libraries send about', UniBib_median, 'Tweets per day.'
print
print 'Oldest account:', UniBib_dateSortList[0]['screen_name'], 'with', UniBib_dateSortList[0]['tweets_per_day'], 'Tweets per day.' 
print 'Latest account:', UniBib_dateSortList[-1]['screen_name'], 'with', UniBib_dateSortList[-1]['tweets_per_day'], 'Tweets per day.' 
print
getInactiveAccounts(UniBib_baseStatsList)
print
print 'Lousiest Tweeter:', UniBib_tweetSortList[0]['screen_name'], 'with', UniBib_tweetSortList[0]['statuses_count'], 'Tweets.' 
print 'SocialMedia Addict:', UniBib_tweetSortList[-1]['screen_name'], 'with', UniBib_tweetSortList[-1]['statuses_count'], 'Tweets.' 
print
printSummary(UniBib_dateSortList)


# <headingcell level=4>

# Public Libraries

# <codecell>

OeBib_median = medianOfTPD(OeBib_baseStatsList)

OeBib_dateSortList = sortingDate(OeBib_baseStatsList)

OeBib_tweetSortList = sortingTweets(OeBib_baseStatsList)


#--------

print 'There are', len(OeBib_libList), 'libraries in this category.'
print
print 'Taken the median, on average these libraries send about', OeBib_median, 'Tweets per day.'
print
print 'Oldest account:', OeBib_dateSortList[0]['screen_name'], 'with', OeBib_dateSortList[0]['tweets_per_day'], 'Tweets per day.' 
print 'Latest account:', OeBib_dateSortList[-1]['screen_name'], 'with', OeBib_dateSortList[-1]['tweets_per_day'], 'Tweets per day.' 
print
getInactiveAccounts(OeBib_baseStatsList)
print
print 'Lousiest Tweeter:', OeBib_tweetSortList[0]['screen_name'], 'with', OeBib_tweetSortList[0]['statuses_count'], 'Tweets.' 
print 'SocialMedia Addict:', OeBib_tweetSortList[-1]['screen_name'], 'with', OeBib_tweetSortList[-1]['statuses_count'], 'Tweets.' 
print
printSummary(OeBib_dateSortList)


# <codecell>


