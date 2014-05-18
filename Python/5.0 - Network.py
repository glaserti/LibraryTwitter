#
# Authentication
#


# Code from MTSW 2Ed.
# cf. https://github.com/ptwobrussell/Mining-the-Social-Web-2nd-Edition

import twitter

def oauth_login():
    # XXX: Go to http://twitter.com/apps/new to create an app and get values
    # for these credentials that you'll need to provide in place of these
    # empty string values that are defined as placeholders.
    # See https://dev.twitter.com/docs/auth/oauth for more information 
    # on Twitter's OAuth implementation.
    
    CONSUMER_KEY = 
    CONSUMER_SECRET =
    OAUTH_TOKEN = 
    OAUTH_TOKEN_SECRET = 
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)
    
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

# Sample usage
twitter_api = oauth_login()    


import sys
import time
from urllib2 import URLError
from httplib import BadStatusLine
import json
import twitter


def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw): 
    
    # A nested helper function that handles common HTTPErrors. Return an updated
    # value for wait_period if the problem is a 500 level error. Block until the
    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
    # for 401 and 404 errors, which requires special handling by the caller.
    
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
    
        if wait_period > 3600: # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e
    
        # See https://dev.twitter.com/docs/error-codes-responses for common codes
    
        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            return None
        elif e.e.code == 429: 
            print >> sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print >> sys.stderr, '...ZzZ...Awake now and trying again.'
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % \
                (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    # End of nested helper function
    
    wait_period = 2 
    error_count = 0 

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0 
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise



from functools import partial
from sys import maxint

def get_friends_followers_ids(twitter_api, screen_name=None, user_id=None,
                              friends_limit=maxint, followers_limit=maxint):
    
    # Must have either screen_name or user_id (logical xor)
    assert (screen_name != None) != (user_id != None), \
    "Must have screen_name or user_id, but not both"
    
    # See https://dev.twitter.com/docs/api/1.1/get/friends/ids and
    # https://dev.twitter.com/docs/api/1.1/get/followers/ids for details
    # on API parameters
    
    get_friends_ids = partial(make_twitter_request, twitter_api.friends.ids, 
                              count=5000)
    get_followers_ids = partial(make_twitter_request, twitter_api.followers.ids, 
                                count=5000)

    friends_ids, followers_ids = [], []
    
    for twitter_api_func, limit, ids, label in [
                    [get_friends_ids, friends_limit, friends_ids, "friends"], 
                    [get_followers_ids, followers_limit, followers_ids, "followers"]
                ]:
        
        if limit == 0: continue
        
        cursor = -1
        while cursor != 0:
        
            # Use make_twitter_request via the partially bound callable...
            if screen_name: 
                response = twitter_api_func(screen_name=screen_name, cursor=cursor)
            else: # user_id
                response = twitter_api_func(user_id=user_id, cursor=cursor)

            if response is not None:
                ids += response['ids']
                cursor = response['next_cursor']
        
            print >> sys.stderr, 'Fetched {0} total {1} ids for {2}'.format(len(ids), 
                                                    label, (user_id or screen_name))
        
            # XXX: You may want to store data during each iteration to provide an 
            # an additional layer of protection from exceptional circumstances
        
            if len(ids) >= limit or response is None:
                break

    # Do something useful with the IDs, like store them to disk...
    return friends_ids[:friends_limit], followers_ids[:followers_limit]



#
# Helper Functions
# 


#importing libraries
import json   #for pretty printing
import time   #for calculating Tweets per day
import operator #for sorting dictionaries
from collections import Counter #for turning lists to dictionaries etc.
    
# helper function: safe the results as a csv-file

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
    outputfile = filename
    keyz = listOfDict[0].keys()
    f = open(outputfile,'w')
    dict_writer = csv.DictWriter(f,keyz)
    dict_writer.writer.writerow(keyz)
    dict_writer.writerows(listOfDict)
    f.close()


# 1. Analyzing the Library's Network

# 1.2. Getting & Calculating Intersection & Differences: are they following back?


# getting Friends & Followers

def getFnFs(screen_name):
    '''
    input = screen name of a library
    output = dictionary with IDs of FnFs, IDs of reciprocal following and stats
    '''
    FnFdict = {}
    FnFdict['screen_name'] = screen_name
     
    friends_ids, followers_ids = get_friends_followers_ids(twitter_api,screen_name)    
        
    FnFdict['friends_ids'] = friends_ids
    FnFdict['followers_ids'] = followers_ids

    # Reciprocal Following?
    FnFdict['friends_ids'], FnFdict['followers_ids'] = set(FnFdict['friends_ids']), set(FnFdict['followers_ids'])
    FnFdict['followBack'] = FnFdict['friends_ids'].intersection(FnFdict['followers_ids'])
    FnFdict['followBackCount'] = len(FnFdict['followBack'])   #Nr of reciprocal following
    FnFdict['XFollowsNotBack'] = len(FnFdict['followers_ids'].difference(FnFdict['friends_ids']))   #Nr of accounts, screen_name is not following back
    FnFdict['NotFollowXBack'] = len(FnFdict['friends_ids'].difference(FnFdict['followers_ids']))   #Nr of accounts which are not following screen_name back
    if len(FnFdict['followers_ids']) != 0:
        FnFdict['activeNotFollowRatio'] = round((1.0*(FnFdict['XFollowsNotBack']))/len(FnFdict['followers_ids']),2)  #Ratio of screen_name not following back
    else:
        FnFdict['activeNotFollowRatio'] = 0
    if len(FnFdict['friends_ids']) != 0:
        FnFdict['passiveNotFollowRatio'] = round((1.0*(FnFdict['NotFollowXBack']))/len(FnFdict['friends_ids']),2)    #Ratio of accounts not following screen_name back
    else:
        FnFdict['passiveNotFollowRatio'] = 0
    FnFdict['friends_ids'] = list(FnFdict['friends_ids']) #convert friends & followers & followBack ids back to list instead of set
    FnFdict['followers_ids'] = list(FnFdict['followers_ids'])
    FnFdict['followBack'] = list(FnFdict['followBack'])
    return FnFdict




def wrapUp(csvFile):
    '''
    input: csv file ("OeBibBasicStats.csv, UniBibBasicStats.csv or NatBibBasicStats.csv") with keys 'screen_name' and 'location'
    output: csv files with dictionaries for each library as <screen_name>_NetWork_<datestamp>.csv
    prints out an short report
    '''
    import datetime
    datestamp = datetime.datetime.now().strftime('%Y-%m-%d')
    
    workLoD = impCSV(csvFile)
    
    
    for i in range(len(workLoD)):
        
        # add screen name & location of the library to dictionary
        workDict = {}
        workDict['screen_name'] = workLoD[i]['screen_name']
        workDict['libLocation'] = workLoD[i]['location']
        
        # Friends & Follower
        workDict.update(getFnFs(workDict['screen_name']))
        
        #creating the filename of the csv with current datestamp and save to csv
        l = [workDict] 
                
        filename = workDict['screen_name'] + '_NetWork_' + datestamp + '.csv'
        exp2CSV(l, filename)
        
        #print report
        print
        s = 'Report for ' + workDict['screen_name'] + ':'
        print s
        print len(s)*'='
        print 
        print 'File saved as', filename
        print
        print 'Friends:', len(workDict['friends_ids'])
        print 'Followers:', len(workDict['followers_ids'])
        print 'followBack:', workDict['followBackCount']
        print 'XFollowsNotBack:', workDict['XFollowsNotBack']
        print 'NotFollowXBack:', workDict['NotFollowXBack']
        print 'activeNotFollowRatio:', workDict['activeNotFollowRatio']
        print 'passiveNotFollowRatio:', workDict['passiveNotFollowRatio']
        print
        print 50*'='
    
