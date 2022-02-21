api_key = 'AIzaSyBJixTpGuWue17mPX1Ia_O7vUcrcvcOdMs'

# we can connect to the YOUTUBE API using this build function
from os import stat
import os
# pip install google-api-python-client
import argparse     # Allows the use of positional arguments. customization of prefix chars. supports variable numbers of parameters for a single option
# import unidecode    # standard for workign with wide range of characters. Each symbol has a codepoint
import pandas as pd
import csv
import sys
import re
import time
from googleapiclient.discovery import build
from datetime import datetime

import xlsxwriter

# Future goal, try to find a way to get this API key (just in case if it fails)
# first define the API_key

api_key = 'AIzaSyBJixTpGuWue17mPX1Ia_O7vUcrcvcOdMs'




def channel_snippet(channel_id, yt):
    """Channel Snippet Function

    Args:
        channel_id (string): Unique channel YouTube ID

    Returns:
        dict: title of channel, description of channel, customUrl, publishedAt, Country location
    """
    snippet = yt.channels().list(part = "snippet", id = channel_id).execute()
    return snippet



def uniqueChannelId_scraper(channelName, yt):
    """uniqueChannelId_scraper function
       If we don't have the unique channel ID for this channel use this function.
       This takes in the Channel Name ("David Dobrik") and find the channel ID.
       However, this cost quota price of 100 units!!!!
       (this should not be run everytime. Only run once on channels we never seen before.)

    Args:
        channelName (String): [Channel Name of Youtuber]

    Returns:
        string: unique ID
    """
    snippet = yt.search().list(part = "snippet", q= channelName, type = 'channel').execute()
    extractedID = snippet['items'][0]['id']['channelId']

    return extractedID



def statsGet(request, countType):
    """getSubsCount function return subscriber count

    Args:
        stats (dict): statistics dictionary

    Returns:
        int: [Subscriber Count]
    """

    
        
    count = request['items'][0]['statistics'][countType]
    print(f"{countType}: {count}")


    return count

def getPlaylistID(request):
    """getPlaylistID returns the unique playlist ID that holds all the videos of the youtube channel

    Args:
        request 

    Returns:
        string : that holds the ID of the playlist 
    """
    id = request['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    return id



def getChannel_title(request):
    title = request['items'][0]['snippet']['title']
    
    return title

def parseISO8601(duration):
    regex= re.compile(r'PT((\d{1,3})H)?((\d{1,3})M)?((\d{1,2})S)?')
    if duration:
        duration = regex.findall(duration)
        if len(duration) > 0:
            _, hours, _, minutes, _, seconds = duration[0]
            duration = [seconds, minutes, hours]
            duration = [int(v) if len(v) > 0 else 0 for v in duration]
            duration = sum([60**p*v for p, v in enumerate(duration)])
        else:
            duration = 30
    else:
        duration = 30
    return duration

def csv_generator(api_key, channel_name = '', channel_unique_id = '', client_name = ''):
    
    
    
    ### Initializing all the values we will pull out
    
    titles = []
    like_count = []
    dislike_count = []
    views = []
    urlList = []
    comment_count = []
    videoIds = []
    publishedDate = []
    video_description = []
    video_length = []
    
    # Connect YouTube Data V3 API 
    try:
        yt = build('youtube', 'v3', developerKey = api_key)
        print("Connected to YouTube API Successfully")

    except:
        print("YouTube API BUILD has failed. Check API_KEY")
    
    
    # call channel_snippet function
    # channelSnippet = channel_snippet(channel_id= channel_unique_id[0])
    # scraped_channelID = channelSnippet['items'][0]['snippet']['channelId']

    # if we don't have the unique Channel ID of the target
    # uniqueChannelId_scraper(channel_name)

    # statistics pull from the corresponding Unique Channel ID
    channel_request = yt.channels().list(part='statistics, contentDetails, snippet', id=channel_unique_id).execute()
    
    total_subscriberCount = statsGet(channel_request, countType= "subscriberCount")
    total_viewCount = statsGet(channel_request, countType="viewCount")
    total_videoCount = statsGet(channel_request, countType= "videoCount")
        
    #we need the channel video playlist id to get all the videos
    #### Content details ID of the channel ####
    # contentDetails = yt.channels().list(part= "contentDetails", id= channel_unique_id[0]).execute()
    # videoPlaylistID = contentDetails['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    playlistID = getPlaylistID(channel_request)
    
    #Getting channel title
    channel_Title = getChannel_title(channel_request)
    
    # Now to extract all the video data#########
    videoList = []
    nextToken = None    # this will allow us to gather more than the limit of 50 searches
    
   
    while True:
        result = yt.playlistItems().list(playlistId= playlistID, maxResults= 50, part= 'snippet', pageToken= nextToken).execute()
        videoList += result['items']
        nextToken = result.get('nextPageToken')
        if nextToken is None:
            break
    
    # print(f"Total number of videos uploaded: {len(videoList)}")

    # get the list of video ID
    videoIdList = list(map(lambda k:k['snippet']['resourceId']['videoId'], videoList))

    print(f"Check the numbers:\n {len(videoList)} == {len(videoIdList)}")

    info_video = []
    for i in range(0, len(videoIdList), 40):
        tmp = (yt).videos().list(id= ','.join(videoIdList[i:i+40]), part= 'statistics, contentDetails').execute()
        info_video += tmp['items']
    
    for count in range(0, len(videoList)):

        titles.append((videoList[count])['snippet']['title'])
        publishedDate.append((videoList[count])['snippet']['publishedAt'])
        video_description.append((videoList[count])['snippet']['description'])
        videoIds.append(videoList[count]['snippet']['resourceId']['videoId'])
        
        video_length.append(info_video[count]['contentDetails']['duration'])
        try:
            like_count.append(int((info_video[count])['statistics']['likeCount']))
        except:
            print(f"Like count was not found")
            like_count.append(int(0))
        try:
            dislike_count.append(int((info_video[count])['statistics']['dislikeCount']))
        except:
            print(f"Dislike count was not found")
            dislike_count.append(int(0))
            
        try:
            views.append(int((info_video[count])['statistics']['viewCount']))
        except:
            print(f"View count was not found")
            views.append(int(0))
            
        try:
            
            comment_count.append(int((info_video[count])['statistics']['commentCount']))
            
        except:
            print("comment count was not found")
            comment_count.append(int(0))
        count += 1
        
        
  
    seconds_list = []
    for i in range(len(video_length)):
        seconds = parseISO8601(video_length[i])
        seconds_list.append(seconds)
        video_length[i]= time.strftime('%H:%M:%S', time.gmtime(seconds))
  
    data = {'channelID': channel_unique_id,'channelName':channel_Title, 'title':titles, 'videoIDs':videoIds, 'video_description': video_description, 'publishedDate':publishedDate, 'likes':like_count, 'dislikes':dislike_count,'views':views, 'comment': comment_count, 'video_length': video_length, 'length_in_seconds': seconds_list}
    df = pd.DataFrame(data)
    print("Creating CSV file...")
    
    # if there is a folder named client_name
    
    if os.path.isdir(client_name):  
        #this is only for linux or mac OS. microsoft uses \
        path = os.path.join(current_PATH, client_name)
        print(path)
        
        df.to_csv(f'{path}/{channel_Title}.csv', index=False)
        
    
    # if there is not a folder named "csv_data" create one
    else:
        os.mkdir(client_name)
        path = os.path.join(current_PATH,client_name)
        df.to_csv(f'{path}/{channel_Title}.csv', index=False)
    
    
    # ### Creating Excel file
    # ### if excel file already exists
    # if os.path.isdir(f"{client_name}.xlsx"):
    #     writer = pd.ExcelWriter(f"{client_name}.xlsx", engine = 'xlsxwriter')
    #     df.to_excel(writer, sheet_name= channel_Title)
        
    # ## if excel file does not exist, create one
    # if os.path.isdir('excelData'):  
    #     #this is only for linux or mac OS. microsoft uses \
    #     path = os.path.join(current_PATH,'excelData')
    #     print(path)
        
    #     df.to_csv(f'{path}/{channel_Title}.xlsx', index=False)
        
    
    # # if there is not a folder named "csv_data" create one
    # else:
    #     os.mkdir('excelData')
    #     path = os.path.join(current_PATH,'excelData')
    #     df.to_excel(f'{path}/{channel_Title}.xlsx', index=False)
    print("Successfully created Excel file with the name")
    return df, channel_Title, total_subscriberCount, total_videoCount, total_viewCount
   



client_name = str(input("Enter our client channel name: \n(no space or special characters. i.e. Laugh Society should be laughSociety)\n"))
current_PATH = os.path.dirname(os.path.abspath(__file__))
print("Current directory: ", current_PATH)


a=os.path.join(current_PATH, 'csv_data')
print(a)
print(os.path.isdir(a))
print("Program start\n")

"""Make sure the text file has one after each line
unique id
unique id
unique id
...
"""
api_key = 'AIzaSyBJixTpGuWue17mPX1Ia_O7vUcrcvcOdMs'

print(f"Generating competitor CSV file for {client_name}...")
writer = pd.ExcelWriter(f"{client_name}.xlsx", engine='xlsxwriter')
with open(f"{client_name}_cList.txt") as f:
    myList = f.read().splitlines()

channelID = []
channelTitle = []
subscriber_list = []
video_list = []
view_list = []
for id in myList:
    print(f"Generating CSV file for {id}...")
    df, channel_title, subCount, vidCount, viewCount = csv_generator(api_key, channel_unique_id=id, client_name=client_name)
    df.to_excel(writer, sheet_name=channel_title[:30])
    channelID.append(id)
    channelTitle.append(channel_title)
    subscriber_list.append(subCount)
    video_list.append(vidCount)
    view_list.append(viewCount)
channelData = {'channelID': channelID, 'channelName': channelTitle, 'totalSubscriber':subscriber_list, 'totalVideo':video_list,'totalView':view_list}
df1 = pd.DataFrame(channelData)
path = os.path.join(current_PATH)
df1.to_csv(f'{path}/channelsData_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv', index=False)

# After the csv files are generated, create a single xlsx file (excel)

writer.save()

