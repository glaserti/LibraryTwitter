#
# Analyzing the Timeline
#


# In this Notebook, the timeline of each account is being analyzed:
# 
# The Function `analyzeTimeline` takes as input the BibTwitter file for each library group and the timestamp of the timeline.json-files. The function returns an csv file for each library group (NatBib\_timeLineStats\_[datestamp].csv).
# 
# The file contains one observation for each tweet with information in these categories:
# 
#    - identification: keys 'screen_name', 'id_str'
#    - date: keys 'created_at', 'tweet_time', 'tweet_weekday', 'tweet_month'
#    - type: keys 'genuine_tweet', 'auto_tweet'
#    - resonance: keys 'favorite_count', , 'rt_count', 'resonance_Factor'  (the resonance factor is the sum of rt_count x 1.0 + favorite_count * 0.5)
#    - content: keys 'has_media', 'has_mention', 'has_url', 'has_hashtag'.
#    
# The file will be extended in Notebook 7.2 Communication with the category 
# 
#    - communication: keys 'is_reply', 'original_is_question', 'reply_is_answer', 'hours_to_answer', 'is_follower', 'follower_local', 'orphan'.
#    
# 


# Helper Functions


#from collections import Counter
#import json

def readJSON(filename):
    import json
    with open(filename) as f:
        data = json.load(f)
        return data

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
    outputfile = filename + '_' + datestamp + '.csv'
    keyz = listOfDict[0].keys()
    f = open(outputfile,'w')
    dict_writer = csv.DictWriter(f,keyz)
    dict_writer.writer.writerow(keyz)
    dict_writer.writerows(listOfDict)
    f.close()


# Function Definition


def analyzeTimeline(bibTwitterfile,timeStamp):
    '''
    input: filename of NatBibTwitter.csv, OeBibTwitter.csv or UniBibTwitter.csv and
    Timestamp = Timestamp of the timeline files
    output: saves a LoD as a csv of the timeline stats
    '''

    # open UniBibTwitter.csv
    f = impCSV(bibTwitterfile)
    l = []                                      # list of screen_names
    LoD = []                                    # List of Dictionary for entire library group

    for i in f:                                 # create list of screen_names/twitter handles
        l.append(i['Twitter'])
    
    for handle in l:
        lod = []                                # list of dictionary for each library
        filename = handle + '_timeline_' + timeStamp + '.json'
        tl = readJSON(filename)
        for e in tl:
            d = {}
            
            # 1. get date
            #
            t = e['created_at']
            t0 = t.find(' ')                    # separates Weekday from Month
            t1 = t.find(' ', t0+1)              # separates Month from day
            t2 = t.find(' ', t1+1)              # separates day from time
            t3 = t.find(':', t2+1)              # separates hour from minute
    
            weekday = t[:t0]
            wd = {'Mon':1, 'Tue':2, 'Wed':3, 'Thu':4, 'Fri':5, 'Sat': 6, 'Sun':7}
            if weekday in wd:
                weekday = wd[weekday]
            month_day = t[t0+1:t1]     
            mon = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun': 6, 'Jul':7, 'Aug':8, 'Sep':9, 
                   'Oct':10, 'Nov':11, 'Dec':12}
            if month_day in mon:
                month_day = mon[month_day]
            hour = t[t2+1:t3]
            
            # 2. RT?
            #
            if 'RT' in e['text'] or 'MT' in e['text']:      # just filter out RT and MT, keep 'via @' though, since these tweets often are considerably altered
                rt = 0                           # if it's a genuine tweet of the library: 1, else: 0
                rt_count = 'NA'                  # don't count the favs & RTs of tweets the library retweeted!
                fav_count = 'NA'
                resFac = 'NA'                    # don't count the tweet content analysis
                hashtag = 'NA'
                mention = 'NA'
                URL = 'NA'
                media = 'NA'
            else:
                rt = 1
                
                # 3. get retweet- & favorite count & calculate resonance factor
                #
                if type(e['retweet_count']) == int:          # "Number of times this Tweet has been retweeted." 
                    rt_count = e['retweet_count']            # "This field is __no longer__ capped at 99 and will not turn into a String for '100+'"   
                elif e['retweet_count'] == '100+':
                    rt_count = 100
                else:
                    rt_count = 0
                fav_count = e['favorite_count']              # "Indicates approximately how many times this Tweet has been "favorited" by Twitter users."
                resFac = rt_count * 1.0 + fav_count * 0.5    # calculating the resonance factor (1.0 for RT, 0.5 for Favs)
                             
                # 4. Content Analysis
                #
                if e['entities']['hashtags'] != []:
                    hashtag = 1
                else:
                    hashtag = 0
                if e['entities']['user_mentions'] != []:
                    mention = 1
                else:
                    mention = 0
                if e['entities']['urls'] != []:
                    URL = 1
                else:
                    URL = 0
                try:
                    m = e['entities']['media']
                    media = 1
                except:
                    media = 0
                
                
            # 5. Auto tweet?
            #
            autoTweetSource = ['twitterfeed', 'wp.com', 'wp-to-twitter', 'tumblr',
                               'instagram', 'blogs.', 'SharePress', 'facebook', 'studivz', 'paper.li']
            for v in autoTweetSource:
                if v in e['source']:
                    at = 1
                    break
                else:
                    at = 0
            
            # 6. Communiacation Analysis
            # is later imported from the ArchiveStats-Files
                                
            # 7. fill dictionary
            #
            d = {'screen_name': handle, 'id_str': e['id_str'], 'created_at': t, 'tweet_weekday': weekday, 'tweet_month': month_day,
                 'tweet_time': hour, 'genuine_tweet': rt, 'auto_tweet': at, 'rt_count': rt_count, 'favorite_count': fav_count,
                 'resonance_Factor': resFac, 'has_hashtag': hashtag, 'has_mention': mention, 'has_url': URL, 'has_media': media}

            lod.append(d)
        LoD += lod
    outputfilename = bibTwitterfile[:-11] + '_timelineStats'
    exp2CSV(LoD, outputfilename)
    return LoD
        


#
# Controll Functions
#


#    
#control functions to check from which sources a tweet was sent
#


#extracting the sources of the tweets
def tweetSource(timeline):
    tweet_source = [sources['source']
                    for sources in timeline]   # List of all sources
    countedSources = Counter(tweet_source) #type = class: Counter({u'xxx': 12, u'yyy': 10, ...}) descending ordered
    countedSources = countedSources.most_common()
    
    #Printing in a table
    # Code adapted from MTSW 2. Ed.
    from prettytable import PrettyTable

    ptLang = PrettyTable(field_names=['Source', 'Count'])
    [ptLang.add_row(kv) for kv in countedSources]
    ptLang.align['Source'], ptLang.align['Count'] = 'l', 'r'
    print str(len(tweet_source)) + ' Tweets were analyzed.'
    print ptLang

    
    
def printTweetFromSource(timeline, source):
    '''
    input: timeline and a word from the source under consideration (e.g. 'wp.com,' or 'tweetfeed')
    output: prints out the index of the tweet in the timeline and the text of the tweet
    '''
    for e in range(len(timeline)):
        if source in timeline[e]['source']:
            print e, timeline[e]['text']
            print

