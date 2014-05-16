# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <rawcell>

# Gets the Conversation (based on the is reply to Key of the libraries timeline) of each tweet and returns the conversation as a LoD with following keys:
# 
# u'hours_to_answer', u'is_follower', u'follower_local', u'original_is_question', u'original_screen_name', 
# u'original_status_id', u'original_text', u'original_time', u'original_user_id', 
# u'orphan', u'reply_is_answer', u'reply_status_id', u'reply_text', u'reply_time'
# 
# 
# Saves a file as csv with the following keys:
# u'hours_to_answer', u'is_follower', u'original_is_question', u'original_time',
# u'orphan', u'reply_is_answer', u'reply_time', u'follower_local'

# <headingcell level=2>

# 1. Function Definitions

# <headingcell level=3>

# 1. Authenticating @ Twitter

# <codecell>


# All functions from MTSW 2 Ed.
#
# (added another error handler  (# 403) in function make_twitter_request
#

import time
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

        if e.e.code == 403:                                                  # added error handler for 403 (TG)
            print >> sys.stderr, 'Encountered 403 Error (Not Authorized)'
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

# <headingcell level=3>

# 2. Helper Functions

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

def exp2CSV(listOfDict, screen_name):
    '''
    arguments = list of dictionaries, filename
    output = saves file to cwd (current working directory)
    '''
    #creating the filename of the csv with current datestamp 
    import datetime
    datestamp = datetime.datetime.now().strftime('%Y-%m-%d')    
    outputfile = screen_name + '_ReplyStats_' + datestamp + '.csv'
    keyz = listOfDict[0].keys()
    f = open(outputfile,'w')
    dict_writer = csv.DictWriter(f,keyz)
    dict_writer.writer.writerow(keyz)
    dict_writer.writerows(listOfDict)
    f.close()
    print 'Conversation statistics was saved as ' + outputfile + '.'

def readJSON(filename):
        import json
        with open(filename) as f:
            data = json.load(f)
            return data

def saveConversationAsJSON(timeline, user_name):
    import io, json, datetime
    datestamp = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = user_name + '_Conversation_' + datestamp + '.json'
    with io.open(filename, 'w', encoding='utf-8') as f:
        f.write(unicode(json.dumps(timeline, ensure_ascii=False)))
    print 'Conversation archive was saved as ' + filename + '.'


def sortLoD(listname, key):
    from operator import itemgetter
    listname.sort(key=itemgetter(key))         # sorting the list over the given key of the dictionary
    return listname
    
# Helper function to search for value in a LoD (bisection search)    
def bisectInLoD(listname, key, value):
    '''
    input: listname of sorted LoD (sortLoD-Function!), key and value
    return index of key-value pair will be returned
    '''
    i_min = 0
    i_max = len(listname) -1
    i_mid = i_min + (i_max-i_min)/2
    if str(value) == str(listname[i_min][key]):
        return i_min
    elif str(value) == str(listname[i_max][key]):
        return i_max
    #elif str(value) == str(listname[i_mid][key]):
    #    return i_mid
    else:
        while str(value) != str(listname[i_mid][key]):
            # print 'i_min', i_min, 'i_mid', i_mid,'i_max', i_max       #   T E S T
            if i_mid == i_max or i_mid == i_min:
                # print 'Some error occured!'                           #   T E S T
                return None
            elif str(value) > str(listname[i_mid][key]):
                i_min = i_mid
                i_mid = i_min + (i_max-i_min)/2            
            elif str(value) < str(listname[i_mid][key]):
                i_max = i_mid
                i_mid = i_min + (i_max-i_min)/2
    return i_mid

# <headingcell level=3>

# 3. Conversation Functions

# <codecell>

def repliedToTweetList(screen_name, timestamp_Timeline, timestamp_Followers):
    '''
    input: screen_name of lib account and timestamps of the libs timeline & Followers
    output: LoD 
    '''
    # 1.
    def getReplies(timeline):
        listOfReplies = []
        for e in timeline:
            d = {}
            if e['in_reply_to_user_id_str'] != None:               # filter out tweets from deleted users accounts
                s = 'via @' + str(e['in_reply_to_screen_name']).lower()    #filter out "via @XXX" retweets
                if s not in e['text'].lower():                             # which are generated via the reply function
                    d['original_user_id'] = e['in_reply_to_user_id_str']
                    d['original_screen_name'] = e['in_reply_to_screen_name']
                    d['original_status_id'] = e['in_reply_to_status_id_str']
                    d['reply_status_id'] = e['id_str']
                    d['reply_time'] = e['created_at']
                    d['reply_text'] = e['text']
                    if d['original_status_id'] != None:
                        d['orphan'] = 0
                    else:
                        d['orphan'] = 1
                    listOfReplies.append(d)
        return listOfReplies

    # 2.
    def separateListOfReplies(listOfReplies):        
        replies = listOfReplies
        repl = replies[:]           # make a copy of replies
        LoNone = []                # replies with NoneType-Elements    
        LoIDs = []    
        for e in repl:
            if e['orphan'] == 0:
                LoIDs.append(e['original_status_id'])
            else:                                         
                LoNone.append(e)     # replies with NoneType-Elements
                replies.remove(e)    # remove the NoneType-Elements from the list
        repl = replies[:]            # re-identify both lists: repl = replies without Nonetypes        
        return LoIDs, repl, LoNone

    # 3.
    def getOriginalTweets(LoIDs):
        LoOriginalTweets = []
        for e in LoIDs:       
            tw = make_twitter_request(twitter_api.statuses.show, _id=e)        # this twitter api request has a rate limit of 180!
            LoOriginalTweets.append(tw)                                        #         
        #print 'Length of LoOriginalTweets is:', len(LoOriginalTweets)
        return LoOriginalTweets

    # 4.
    def newDict(LoOriginalTweets):
        # try to get original text and time of tweet, if tweet ID is not valid, pass
        LoDic = []
        for i in LoOriginalTweets:        
            d = {}
            try:          # try to get original text and time of tweet, if tweet ID is not valid, pass
                d['original_text'] = i['text']   #.encode('utf-8')
                d['original_time'] = i['created_at']
                d['original_status_id'] = i['id']
                LoDic.append(d)
            except:
                print 'Trouble with this tweet (It is not included in further examination!):', i
                pass 
        #print len(LoDic)            # T e s t
        #print LoDic[0].keys()       # T e s t
        return LoDic
    
    # 5.
    def clusterValid(LoDic, repl):
        import time
        repl = sortLoD(repl, 'original_status_id')     # sort repl    
        #print 'len repl', len(repl)                                 # T e s t
        
        for n in LoDic:
            i = bisectInLoD(repl, 'original_status_id', n['original_status_id'])  # search for id in repl            
            n.update(repl[i])
            repl.pop(i)                            # remove item from list after it's appended to LoDic
            if screen_name in n['original_text']:       # test if reply is answer
                n['reply_is_answer'] = 1
            else:
                n['reply_is_answer'] = 0        
            
            if '?' in n['original_text']:    # check if original tweet was a question (included an '?')
                n['original_is_question'] = 1
            else:
                n['original_is_question'] = 0
                
            # calculate  reaction time to reply
            #calculating Tweets per day and year
            t0 = time.mktime(time.strptime(n['original_time'], "%a %b %d %H:%M:%S +0000 %Y"))#returns date in seconds (from 1970-01-01)
            t1 = time.mktime(time.strptime(n['reply_time'], "%a %b %d %H:%M:%S +0000 %Y"))
            diff = round(float((t1 - t0))/3600,1) #calculates the difference in hours (3600 sec per hour)
            n['hours_to_answer'] = diff            
                    
            #print len(n.keys())        # T e s t
        #print n.keys()                # T e s t
        return LoDic, repl
    
    # 6.    
    def clusterNoneTypes(repl):
        for n in repl:        
            n['original_text'] = '-'                        
            n['original_time'] = '-'                 
            n['reply_is_answer'] = '-'               
            n['hours_to_answer'] = '-'
            n['original_is_question'] = '-'
            n['orphan'] = 1
        return repl

    # 7.
    def isFollower(repl):    
        filenameFLW = screen_name + '_Followers_' + timestamp_Followers + '.csv'
        flw = impCSV(filenameFLW)        
        flw = sortLoD(flw, 'followers_user_id')    
        cluster = ['librarian', 'Bib', 'publisher']
        for n in repl:
            i = bisectInLoD(flw, 'followers_user_id', n['original_user_id'])
            if type(i) == int:
                if flw[i]['cluster'] in cluster:                
                    n['is_follower'] = 'professional'
                else:
                    n['is_follower'] = 'nonprof'
                if 'local' in flw[i]['followers_location']:
                    n['follower_local'] = 1
                else:
                    n['follower_local'] = 0
            else:
                n['is_follower'] = 0 
                n['follower_local'] = 0
        return repl
    

    
    filenameTL = screen_name + '_timeline_' + timestamp_Timeline + '.json'
         
    tl = readJSON(filenameTL)                                        # 0.  get timeline   
    listOfReplies = getReplies(tl)                                   # 1.0  get the replies from TL
    if len(listOfReplies) > 0:                                       # 1.1 if there are replies at all  
        LoIDs, repl, LoNone = separateListOfReplies(listOfReplies)   # 2.  get list of valid status IDs of original tweets
        LoOriginalTweets = getOriginalTweets(LoIDs)                  # 3.  make Twitter API request to get original Tweets
                                                                     #     only 180 Tweets per 15 min!!
        LoDic = newDict(LoOriginalTweets)                            # 4.  try to get original text and time of tweet
        LoDic, repl = clusterValid(LoDic, repl)                      # 5.  cluster the valid tweets
        repl += LoNone                                               # 6.0 concatenate both NoneType lists
        repl = clusterNoneTypes(repl)                                # 6.1 cluster the NoneType tweets
        repl += LoDic                                                # 7.0 concatenate Valid & NoneType lists
        repl = isFollower(repl)                                      # 7.1 check if replied to are followers
        saveConversationAsJSON(repl, screen_name)                    # 8.  save as json-file
    else:                                                            # 9. create LoD for non replying libs
        edl = ['hours_to_answer', 'is_follower', 'original_time',
               'original_is_question', 'orphan', 'reply_is_answer', 
               'reply_time', 'follower_local', 'reply_status_id']
        repl = []
        ed = {}
        for e in edl:
            ed[e] = '-'
        repl.append(ed)
    return repl                                                  # 10. return the LoD
        
    
def saveReplyStats(repl,screen_name):    
    lod = []    
    for e in repl:
        d = {}
        d['hours_to_answer'] = e['hours_to_answer']
        d['is_follower'] = e['is_follower']
        d['follower_local'] = e['follower_local']
        d['original_is_question'] = e['original_is_question']
        d['original_time'] = e['original_time']
        d['orphan'] = e['orphan']
        d['reply_is_answer'] = e['reply_is_answer']
        d['reply_time'] = e['reply_time']
        d['reply_status_id'] =  e['reply_status_id']                           
        lod.append(d)
    exp2CSV(lod, screen_name) 
   

# <headingcell level=3>

# 4. Reporting Functions

# <codecell>


def reportFollower(rep):
    p = 0
    n = 0
    nf = 0
    l = 0
    for e in rep:
        if e['is_follower'] == 'professional':
            p += 1
        elif e['is_follower'] == 'nonprof':
            n += 1
        elif e['is_follower'] == 0:
            nf += 1
        else:
            print 'Take a closer look at', e
            print
        if e['follower_local'] == 1:
            l += 1
    print 'From the total of ' + str(len(rep)) + ', the replied to accounts belonged to following groups:'
    print p, 'professionals'
    print n, 'non professionals'
    print nf, 'non followers'
    print l, 'of these are locals.'


def reactionReport(rep):
    antime = 0
    orph = 0
    quest = 0
    ans = 0
    
    
    for e in rep:
        # calculate mean of time to answer
        if e['orphan'] == 1:
            orph += 1
        else:
            if type(e['hours_to_answer']) == float:
                antime += e['hours_to_answer']
            
            # calculate answers to questions    
            if e['original_is_question'] == 1:
                quest += 1
            if e['reply_is_answer'] == 1:
                ans += 1
        
        
    print 'It took about', round(antime/(len(rep) - orph),1), ' hours in average to reply to a tweet.'
    print orph, "of the original tweets were no longer accessible (were deleted)"
    print "          - and thus couldn't be evaluated."  
    print "Of these tweets,", quest, "were questions (i.e. a ratio of ", round(float(quest)/(len(rep) - orph),2), "),",
    print         ans, "were answers to questions."
    
    
    

# <headingcell level=3>

# 3. Wrap Up Function

# <codecell>

def getConversations(Twitterfile, timestamp_Timeline, timestamp_Followers):
    '''
    input: Twitterfile, timestamp_Timeline, timestamp_Followers
    output: returns LoD as a csv with keys u'hours_to_answer', u'is_follower', 
    u'original_is_question', u'original_time',u'orphan', u'reply_is_answer', 
    u'reply_time', u'follower_local'
    '''
        
    f = impCSV(Twitterfile)
    listOfScreenNames = []
    for e in f:
        listOfScreenNames.append(e['Twitter'])                # get Twitter handel of the library
    for sn in listOfScreenNames:
        convers = repliedToTweetList(sn, timestamp_Timeline, timestamp_Followers)
        saveReplyStats(convers, sn)

# <headingcell level=2>

# 2. Function Calls

# <codecell>

getConversations('NatBibTwitter2.csv', '2014-04-07', '2014-04-07')

# <codecell>

getConversations('UniBibTwitter.csv', '2014-04-07', '2014-04-06')

# <codecell>

getConversations('OeBibTwitter.csv', '2014-04-07', '2014-04-06')

# <codecell>


