#
# Extending the TimelineStatistic
#


# This Notebook appends the TimelineStatsfile with ReplyStats-file, thus adding the Communication category to the TLstats file, with the keys:
# 
#    - 'is_reply', (1; if there is no corresponding id in the TLS-file, the value is 0, and the other variables are set to: 'NA')
#    - 'original_is_question', (if there is a questionmark in the original post: 1, else: 0) 
#    - 'reply_is_answer', (when original tweet contained the screen_name of the library: 1, else: 0)
#    - 'hours_to_answer', 
#    - 'is_follower', (when original account is a follower of the library: professional or nonprof, else 0)
#    - 'follower_local', (when original account is a follower of the library and is local: 1, else 0)
#    - 'orphan' (when the original tweet is no longer accessible: 1, else: 0)
#    
# 


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
    outputfile = screen_name + '_timelineStats_' + datestamp + '.csv'
    keyz = listOfDict[0].keys()
    f = open(outputfile,'w')
    dict_writer = csv.DictWriter(f,keyz)
    dict_writer.writer.writerow(keyz)
    dict_writer.writerows(listOfDict)
    f.close()
    print 'Conversation statistics was saved as ' + outputfile + '.'

        
def sortLoD(listname, key):
    from operator import itemgetter
    listname.sort(key=itemgetter(key))         # sorting the list over the given key of the dictionary
    return listname

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



def updateTLSConv(Twitterfile, dateTLS, dateRStats):
#Twitterfile to get handles
    workLoD = []
    # open TLS
    tlsfile = Twitterfile[:-11] + '_timelineStats_' + dateTLS + '.csv'
    tls = impCSV(tlsfile)
    
    f = impCSV(Twitterfile)
    #listHandles = []
    for e in f:
        handle = e['Twitter']                # get Twitter handel of the library
        #listHandles.append(handle)
        RSfile = handle + '_ReplyStats_' + dateRStats + '.csv'
    
    # open ReplyStats
        try:
            RStats = impCSV(RSfile)
            # sort ReplyStats
            RStats = sortLoD(RStats, 'reply_status_id')
    
            # for e in TLS:
            for i in range(len(tls)):
                if tls[i]['screen_name'] == handle:
                    workDic = tls[i]
                    idx = bisectInLoD(RStats, 'reply_status_id', tls[i]['id_str'])
                    if idx != None:                    
                        workDic.update(RStats[idx])
                        workDic.pop('reply_time', None)
                        workDic.pop('reply_status_id', None)
                        workDic.pop('original_time', None)
                        workDic['is_reply'] = 1
                    else:
                        workDic['original_is_question'] = 'NA'
                        workDic['reply_is_answer'] = 'NA'
                        workDic['orphan'] = 'NA'	
                        workDic['hours_to_answer'] = 'NA'	
                        workDic['is_follower'] = 'NA'
                        workDic['follower_local'] = 'NA'	
                        workDic['is_reply'] = 0
                    workLoD.append(workDic)
            
        except:
            for i in range(len(tls)):
                if tls[i]['screen_name'] == handle:
                    print 'File not accessible:', RSfile
                    for i in range(len(tls)): 
                        workDic = tls[i]
                        workDic['original_is_question'] = 'NA'
                        workDic['reply_is_answer'] = 'NA'
                        workDic['orphan'] = 'NA'	
                        workDic['hours_to_answer'] = 'NA'	
                        workDic['is_follower'] = 'NA'
                        workDic['follower_local'] = 'NA'	
                        workDic['is_reply'] = 0
                        workLoD.append(workDic)
        #print len(workLoD)
    exp2CSV(workLoD, Twitterfile[:-11])
    
    return workLoD

