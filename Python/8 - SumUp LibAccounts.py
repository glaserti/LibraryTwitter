# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Sum up the LibAccount Stats

# <markdowncell>

# In this Notebook, the statistics of the library accounts is being summarized. The `libTwitterStats`-function takes as arguments 
# 
#    1. the basicStats-file from Notebook 4,
#    1. the network-file from Notebook 5.0,
#    1. the friends- and followers-files from Notebook 5.1, and
#    1. the timeLineStats-file from Notebook 7.1
#    
# The file will be saved as NatBib_libTwitterStats_2014-04-09.csv etc.

# <headingcell level=2>

# Function Definitions

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
    keyz = listOfDict[0].keys()
    f = open(filename,'w')
    dict_writer = csv.DictWriter(f,keyz)
    dict_writer.writer.writerow(keyz)
    dict_writer.writerows(listOfDict)
    f.close()

# <codecell>

def libTwitterStats(basicStatsFile, NetWork_datestamp, Friends_datestamp, timelineStats_datestamp):
    # 1. NatBib_BasicStats_2014-03-24.csv
    # all keys
    filename = basicStatsFile
    datestampNW = NetWork_datestamp               # datestamp of Networkfile
    datestampFriends = Friends_datestamp
    datestampTLS = timelineStats_datestamp
    LoD = []
    bs = impCSV(filename)
    print 'Number of libraries:', len(bs)
    
    # 2. open corresponding Network file for each library
    for e in bs:
        sn = e['screen_name']
        nwfn = sn + '_NetWork_' + datestampNW + '.csv'
        tweets = int(e['statuses_count'])
        nwdic = impCSV(nwfn)[0]
        nwdic.pop('screen_name', None)
        nwdic.pop('libLocation', None)
        nwdic.pop('followBack', None)
        nwdic.pop('followers_ids', None)
        nwdic.pop('friends_ids', None)
        e.update(nwdic)                        # update the dictionary e
     
        # 3. friends file offnen
        friendsFileName = sn + '_Friends_' + datestampFriends + '.csv'
        
        try:      
            friends = impCSV(friendsFileName)
            friendsDic = {}
            from collections import Counter
            LoCluster = []
            LoLocation = []
            for i in friends:
                LoCluster.append(i['cluster'])
                LoLocation.append(i['friends_location'])
            cluster = Counter(LoCluster)  
            location = Counter(LoLocation)
        except:
            friendsDic = {'friend_librarian': 'NA', 'friend_library': 'NA', 'friend_publisher': 'NA',
                          'friend_varia': 'NA', 'friend_without_description': 'NA', 'friend_local': 'NA',
                          'friend_without_place': 'NA', 'friend_other_place': 'NA'}
        
        friendsDic['friend_librarian'] = cluster['librarian']
        friendsDic['friend_library'] = cluster['Bib']
        friendsDic['friend_publisher'] = cluster['publisher']
        friendsDic['friend_varia'] = cluster['varia']
        friendsDic['friend_without_description'] = cluster['--']
        friendsDic['friend_local'] = location['local']
        friendsDic['friend_without_place'] = location['--']
        friendsDic['friend_other_place'] = len(friends) - (friendsDic['friend_local'] + friendsDic['friend_without_place'])
        e.update(friendsDic)                        # update the dictionary e
    
    
        # 4. follower file offnen
        followersFileName = sn + '_Followers_' + datestampFriends + '.csv'
        followers = impCSV(followersFileName)
        dFol = {}
        from collections import Counter
        LoClusterFol = []
        LoLocationFol = []
        for i in followers:
            LoClusterFol.append(i['cluster'])
            LoLocationFol.append(i['followers_location'])
        clusterFol = Counter(LoClusterFol)  
        locationFol = Counter(LoLocationFol)
        dFol['follower_librarian'] = clusterFol['librarian']
        dFol['follower_library'] = clusterFol['Bib']
        dFol['follower_publisher'] = clusterFol['publisher']
        dFol['follower_varia'] = clusterFol['varia']
        dFol['follower_without_description'] = clusterFol['--']
        dFol['follower_local'] = locationFol['local']
        dFol['follower_without_place'] = locationFol['--']
        dFol['follower_other_place'] = len(followers) - (dFol['follower_local'] + dFol['follower_without_place'])    
        e.update(dFol)                        # update the dictionary e
    
        
        # 5. open UniBib_timelineStats_2014-04-02.csv
        tlfilename = filename[:-26] + '_timelineStats_' + datestampTLS + '.csv'
        tlstats = impCSV(tlfilename)
        dTLS = {}
        
        #tweets = 0
        isGenuine = 0
        
        hasMedia = 0
        hasURL = 0
        hasMention = 0
        hasHash = 0
        hasEntity = 0
        resFac = 0
        isFav = 0
        isRT = 0
        
        isReply = 0
        repNoOrph = 0
        hrs2a = 0
        
        isAuto = 0
        
        for ix in tlstats:
            if ix['screen_name'].lower() == sn.lower():
                #tweets += 1
                if int(ix['genuine_tweet']) == 1:      # all the following stats shall only be calculated
                    isGenuine += 1                     # for the genuine tweets of the library
                    hasMedia += int(ix['has_media'])
                    hasURL += int(ix['has_url'])
                    hasMention += int(ix['has_mention'])
                    hasHash += int(ix['has_hashtag'])
                    if int(ix['has_media']) + int(ix['has_url']) + int(ix['has_mention']) + int(ix['has_hashtag']) > 0:
                        hasEntity += 1
                    
                    resFac += float(ix['resonance_Factor']) 
                    
                    if int(ix['favorite_count']) > 0:
                        isFav += 1
                    if int(ix['rt_count']) > 0:
                        isRT += 1
                    
                    if int(ix['is_reply']) == 1:
                        isReply += 1
                        if int(ix['orphan']) == 0:
                            repNoOrph += 1                         # to calculate average of reply time, the
                            hrs2a += float(ix['hours_to_answer'])  # orphaned replies can't be taken into account
                    
                    if int(ix['auto_tweet']) == 1:
                        isAuto += 1

        if repNoOrph == 0:
            dTLS['avg_hours_to_answer'] = 0
        else:
            dTLS['avg_hours_to_answer'] = round(float(hrs2a)/repNoOrph,2)
                
        if isGenuine > 0:        
            dTLS['genuine_tweet_ratio'] = round(float(isGenuine)/tweets,2)   
            dTLS['avg_has_media'] = round(float(hasMedia)/isGenuine,2)
            dTLS['avg_has_url'] = round(float(hasURL)/isGenuine,2)
            dTLS['avg_has_mention'] = round(float(hasMention)/isGenuine,2)
            dTLS['avg_has_hashtag'] = round(float(hasHash)/isGenuine,2)
            dTLS['avg_has_entity'] = round(float(hasEntity)/isGenuine,2)
            dTLS['avg_resonanceFactor'] = round(float(resFac)/isGenuine,2)
            dTLS['avg_Favs'] = round(float(isFav)/isGenuine,2)
            dTLS['avg_RTs'] = round(float(isRT)/isGenuine,2)        
            dTLS['replies_ratio'] = round(float(isReply)/isGenuine,2)
            dTLS['auto_tweet_ratio'] = round(float(isAuto)/tweets,2)
        else:
            dTLS['genuine_tweet_ratio'] = 0.0  
            dTLS['avg_has_media'] = 'NA'
            dTLS['avg_has_url'] = 'NA'
            dTLS['avg_has_mention'] = 'NA'
            dTLS['avg_has_hashtag'] = 'NA'
            dTLS['avg_has_entity'] = 'NA'
            dTLS['avg_resonanceFactor'] = 'NA'
            dTLS['avg_Favs'] = 'NA'
            dTLS['avg_RTs'] = 'NA'       
            dTLS['replies_ratio'] = 'NA'
            dTLS['auto_tweet_ratio'] = 'NA'

        e.update(dTLS)                        # update the dictionary e
             
        # append the List of Dictionaries with the new dictionary
        LoD.append(e)
    
    import datetime
    datestamp = datetime.datetime.now().strftime('%Y-%m-%d')    
    libTwitterStatsFilename = filename[:-26] + '_libTwitterStats_' + datestamp + '.csv'
    exp2CSV(LoD, libTwitterStatsFilename)
    print "The summary was saved as " + libTwitterStatsFilename + "."
    return LoD
    
    

# <headingcell level=2>

# Function Calls

# <codecell>

NatBib = libTwitterStats('NatBib_BasicStats_2014-04-07.csv', '2014-04-06','2014-04-07','2014-04-09')

# <codecell>

UniBib = libTwitterStats('UniBib_BasicStats_2014-04-07.csv', '2014-04-06','2014-04-06','2014-04-09')

# <codecell>

OeBib = libTwitterStats('OeBib_BasicStats_2014-04-07.csv', '2014-04-06','2014-04-06','2014-04-09')

# <codecell>


