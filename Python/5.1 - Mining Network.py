# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# The function call of __FnFMining__ wraps up all the helper functions in this Notebook.
# It's using the IDs harvested in the last Notebook and saved in the NetWork-files to collect data about these IDs.
# 
# The function takes as input the twitterfiles of each category (NatBibTwitter.csv etc.), opens for each library in this file the corresponding NetWork-[datestamp]-file and returns
# 
#    - for each library
#       - a csv-file with the Friends-IDs and Data (if the library is following other accounts; there are some libraries which are actually not following)
#       - a csv-file with the Followers-IDs and Data
# 
#    - a list of the files for each library category, called NatBib_Files.txt etc.
#    - also an error message for user IDs which could not be accessed. This is, most of the time, because the accounts were deleted. One could check these IDs via a service as e.g. http://tweeterid.com.
#    
# The Friends and Followers files contain List of Dictionaries (LoD) with the keys: friends_description, friends_user_id, friends_location, friends_screen_name, and followers_description, followers_user_id, followers_location, followers_screen_name respectively.

# <codecell>

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

# <codecell>

#importing libraries
import json   #for pretty printing
import time   #for calculating Tweets per day
import operator #for sorting dictionaries
from collections import Counter #for turning lists to dictionaries etc.
from prettytable import PrettyTable   #for pretty printing in a table


# helper function Prettyprint taken from MTSW 2Ed.

def prettyPrint(Sp_1, Sp_2, counted_list_of_tuples):
    ptLang = PrettyTable(field_names=[Sp_1, Sp_2])
    [ptLang.add_row(kv) for kv in counted_list_of_tuples]
    ptLang.align[Sp_1], ptLang.align[Sp_2] = 'l', 'r'
    print ptLang
    
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

# <codecell>

# Both functions from MTSW 2 Ed.

import sys
from urllib2 import URLError
from httplib import BadStatusLine

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

# See https://dev.twitter.com/docs/api/1.1/get/users/lookup for 
# twitter_api.users.lookup


def get_user_profile(twitter_api, screen_names=None, user_ids=None):
   
    # Must have either screen_name or user_id (logical xor)
    assert (screen_names != None) != (user_ids != None), \
    "Must have screen_names or user_ids, but not both"
    
    items_to_info = {}

    items = screen_names or user_ids
    
    while len(items) > 0:

        # Process 100 items at a time per the API specifications for /users/lookup.
        # See https://dev.twitter.com/docs/api/1.1/get/users/lookup for details.
        
        items_str = ','.join([str(item) for item in items[:100]])
        items = items[100:]

        if screen_names:
            response = make_twitter_request(twitter_api.users.lookup, 
                                            screen_name=items_str)
        else: # user_ids
            response = make_twitter_request(twitter_api.users.lookup, 
                                            user_id=items_str)
    
        for user_info in response:
            if screen_names:
                items_to_info[user_info['screen_name']] = user_info
            else: # user_ids
                items_to_info[user_info['id']] = user_info

    return items_to_info

# <codecell>

def lookUpProfilesFriends(listOfIDs):
    ''' 
    input: list of IDs of Friends or Followers
    output: list dictionaries with keys 'user_id', 'screen_name', 'location', 'description'
    '''
    LoD = []
    errorIDs = []
    
    profiles = get_user_profile(twitter_api, user_ids=listOfIDs)
    try:
        for e in listOfIDs:
            infoDic = {}
            infoDic['friends_user_id'] = e
            infoDic['friends_screen_name'] = profiles[e]['screen_name']
            infoDic['friends_location'] = (profiles[e]['location']).encode('utf-8')
            infoDic['friends_description'] = (profiles[e]['description']).encode('utf-8')
            LoD.append(infoDic)
    except:
        errorIDs.append(e)
    if len(errorIDs) > 0:
        print
        print 'Error for these IDs:', errorIDs
        print
    return LoD


def lookUpProfilesFollowers(listOfIDs):
    ''' 
    input: list of IDs of Friends or Followers
    output: list dictionaries with keys 'user_id', 'screen_name', 'location', 'description'
    '''
    LoD = []
    errorIDs = []
    profiles = get_user_profile(twitter_api, user_ids=listOfIDs)
    
    try:
        for e in listOfIDs:
            infoDic = {}
            infoDic['followers_user_id'] = e
            infoDic['followers_screen_name'] = profiles[e]['screen_name']
            infoDic['followers_location'] = (profiles[e]['location']).encode('utf-8')
            infoDic['followers_description'] = (profiles[e]['description']).encode('utf-8')
            LoD.append(infoDic)
    except:
        errorIDs.append(e)
    if len(errorIDs) > 0:
        print 'Error for these IDs:', errorIDs
    
    return LoD


def wrapLookUp(dictOfFnFs):
    '''
    input: dict of FnFs of a lib (with keys 'followers_ids', 'friends_ids', 'screen_name' (of the lib)
    output: a list of filenames
    saves two files: <twitterhandel>_Friends_<datestamp>.csv and <twitterhandel>_Followers_<datestamp>.csv
    '''
    f1 = dictOfFnFs['friends_ids']
    f2 = dictOfFnFs['followers_ids']
    
    #in case the list is converted to a str
    if type(f1) == str and f1 != '[]':
        f11 = f1.strip('[]')
        f1 = [int(s) for s in f11.split(',')]
    else:
        pass
    if type(f2) == str and f2 != '[]':
        f21 = f2.strip('[]')
        f2 = [int(s) for s in f21.split(',')]
    else:
        pass
    
    if len(f1) > 0 and type(f1) == list:
        friends = lookUpProfilesFriends(f1)
    else:
        friends = []
    if len(f2) > 0 and type(f2) == list:
        followers = lookUpProfilesFollowers(f2)
    else:
        followers = []
            
    #creating the filename of the csv with current datestamp 
    import datetime
    datestamp = datetime.datetime.now().strftime('%Y-%m-%d')
    filename_friends = dictOfFnFs['screen_name'] + '_Friends_' + datestamp + '.csv'
    filename_followers = dictOfFnFs['screen_name'] + '_Followers_' + datestamp + '.csv'
    LoFilenames = [] # [filename_friends, filename_followers]
    
    #export as CSV to CWD
    if len(friends) > 0:
        exp2CSV(friends, filename_friends)
        LoFilenames.append(filename_friends)
    if len(followers) > 0:
        exp2CSV(followers, filename_followers)
        LoFilenames.append(filename_followers)
  
    return LoFilenames

# <codecell>

def FnFMining(Twitterfile, datestamp):
    '''
    input: the NatBibTwitter.csv etc. filenames and the datestamp of the'_NetWork_2014-03-11.csv' file.
    (the library Twitter name will be added).
    '''
    import pickle                      # for saving the list to a file
    
    f = impCSV(Twitterfile)
    listOfFilenames = []
    for e in f:
        n = e['Twitter']                # get Twitter handel of the library
        filename = n + '_NetWork_' + datestamp + '.csv' # create the filename for the library
        print filename
        b = impCSV(filename)            # import this file
        p = wrapLookUp(b[0])            # get description etc. for the FnFs of the library
        
        print p                        # print the filenames for each library
        listOfFilenames += p

    # for saving the list to a file    
    filename2 = Twitterfile[:-11] + '_Files.txt'   # creating a filename like UniBibFiles.txt
    print filename2
    with open(filename2, 'wb') as f:
        pickle.dump(listOfFilenames, f)
        

# <headingcell level=3>

# Function Calls

# <headingcell level=4>

# National Libraries

# <codecell>

FnFMining('NatBibTwitter2.csv', '2014-04-06')

# <headingcell level=4>

# University Libraries

# <codecell>

FnFMining('UniBibTwitter2.csv', '2014-04-06')

# <headingcell level=4>

# Public Libraries

# <codecell>

FnFMining('OeBibTwitter2.csv', '2014-04-06')

# <codecell>


