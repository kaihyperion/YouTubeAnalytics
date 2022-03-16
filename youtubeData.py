import os
import argparse
import time
import configparser
from googleapiclient.discovery import build
import generate_conf
import re
import pandas as pd
import xlsxwriter
from datetime import datetime
config = configparser.ConfigParser()
config.read('conf.ini')

class YouTubeData:
    
    def __init__(self, credentials):

        
        ### configuration settings
        self.api_name = config.get('YouTube Data', 'api_service_name')
        self.api_key = config.get('YouTube Data', 'API_KEY')
        self.api_version = config.get('YouTube Data', 'api_version')
        self.credentials = credentials
        
        # build for API calls
        self.build = None
        
        # api call settings
        self.part = 'statistics, contentDetails, snippet'
        
        #Save settings
        self.current_PATH = os.path.dirname(os.path.abspath(__file__))
        self.target_PATH = os.path.join(self.current_PATH, 'data')
        ## Channel Data
        self.response = None
        self.channelID = None
        self.channelName = None
        
        self.total_subscriberCount = 0
        self.total_viewCount = 0
        self.total_videoCount = 0
        
        self.playlistID = None
        
        
        
        self.videoList = None   # holds the videoList
        self.videoIDList = None  #holds the unique Video ID list. used for fetching individual video data
        self.videoDataList = None #holds Data for each individual video
        
        
        
        self.titles = []
        self.like_count = []
        self.dislike_count = []
        self.views = []
        self.urlList = []
        self.comment_count = []
        self.videoIds = []
        self.publishedDate = []
        self.video_description = []
        self.video_length = []
        self.video_thumbnails = []
        
        self.seconds_list = []
        
        
    def api_build(self):
        """Using Google API Client, connect with API DATA V3
        
        Returns: None
        """ 
        self.build = build(serviceName = self.api_name, version = self.api_version, credentials = self.credentials)
        
    
    def xslxWriter(self):
        return pd.ExcelWriter(f"{self.channelName}.xlsx", engine='xlsxwriter')
    ##########################################
    ### Functions for Channel Related Data ###
    ##########################################
    
    def getChannelIDs(self, channelName):
        """
        Use if you don't know channel ID
        Retrieves a list of channel ID given channel name
        Given a string of Channel name, it will do a YouTube Search
        It will search for first 5 related youtube channel with the given channel Name

        Args:
            channelName (str): ie. David Dobrik or Powder Blue

        Returns:
            List: list of channel ID
            list: list of channel description string
            list: list of thumnail URL  
        """
        channelId_list = []
        description_list = []
        thumbnail_list = []
        
        response = self.build.search().list(part = 'snippet', q= str(channelName), type = 'channel').execute()
        
        for i in range(5):
            
            if response['items'][i]:
                channelId = response['items'][i]['id']['channelId']
                description = response['items'][i]['snippet']['description']
                thumbnail_url = response['items'][i]['snippet']['thumbnails']['default']
                
                channelId_list.append(channelId)
                description_list.append(description)
                thumbnail_list.append(thumbnail_url)
        
        return channelId_list, description_list, thumbnail_list
    
    
    def getMyChannelID(self):
        response = self.build.channels().list(part = 'snippet, contentDetails, statistics',
                                   mine = True).execute()
        return response['items'][0]['id']
    def setChannelID(self, channelID):
        """Sets the channel ID

        Args:
            channelID (str): Unique YouTube Channel ID i.e. UCxxxxx
        """
        
        self.channelID = channelID
    
    
    
    def setChannelName(self, channelName):
        """Sets the ChannelNameq

        Args:
            channelName (str): Channel Name of the YouTuber
        """
        self.channelName = channelName
            
    
    
    
    def getChannelRequest(self):
        response = self.build.channels().list(part=self.part, id=self.channelID).execute()
        self.response = response
        
    def getChannelName(self):
        """If we have response from getChannelRequest, we can also get Channel Name
        """
        self.setChannelName(self.response['items'][0]['snippet']['title'])
        
    def getStatistics(self):
        """Retrieves Statistics of the channel
        View Count
        Subscriber Count
        hiddenSubscriberCount: False or count
        videoCount
        """
        response = self.response['items'][0]['statistics']
        
        # Sets the following class variables
        self.total_viewCount = response['viewCount']
        self.total_subscriberCount = response['subscriberCount']
        self.total_videoCount = response['videoCount']
        

    
    
    def getPlaylistID(self):
        """playlistID is a unique playlist ID that HOLDS ALL THE VIDEOS
        of the specified YouTube Channel ID
        """
        self.playlistID = self.response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        return self.playlistID
    
    
    def setVideoList(self):
        """This sets VideoList
        It holds the following
        id: ID of the video
        title: title of the video
        description: description of the video
        thumbnails: of the video
        """
        videoList = []
        nextToken = None
        
        while True:
            result = self.build.playlistItems().list(playlistId = self.playlistID,
                                                     maxResults = 50,
                                                     part = 'snippet',
                                                     pageToken = nextToken).execute()
            videoList += result['items']
            nextToken = result.get('nextPageToken')
            if nextToken is None:
                break
        
        self.videoList = videoList      
        
        
    def setVideoIDList(self):
        """Retrieves and Sets the VideoIDList
        This holds all the unique individual video ID numbers
        **** RUN setVideoList first!!!
        """
        self.videoIDList = list(map(lambda k:k['snippet']['resourceId']['videoId'], self.videoList))

    
    
    def setVideoDataList(self):
        info_video = []
        
        
        for i in range(0, len(self.videoIDList), 40):
            
            tmp = self.build.videos().list(id= ','.join(self.videoIDList[i:i+40]), part= 'statistics, contentDetails').execute()
            info_video += tmp['items']
            
        self.videoDataList = info_video
        
        
        
    
    def videoDataParser(self):
        for count in range(0, len(self.videoIDList)):
            self.titles.append((self.videoList[count])['snippet']['title'])
            self.publishedDate.append((self.videoList[count])['snippet']['publishedAt'])
            self.video_description.append((self.videoList[count])['snippet']['description'])
            self.videoIds.append(self.videoList[count]['snippet']['resourceId']['videoId'])
            self.video_thumbnails.append(self.videoList[count]['snippet']['thumbnails']['high']['url'])
            self.video_length.append(self.videoDataList[count]['contentDetails']['duration'])
            try:
                self.like_count.append(int((self.videoDataList[count])['statistics']['likeCount']))
            except:
                print(f"Like count was not found")
                self.like_count.append(int(0))
            try:
                self.dislike_count.append(int((self.videoDataList[count])['statistics']['dislikeCount']))
            except:
                print(f"Dislike count was not found")
                self.dislike_count.append(int(0))
                
            try:
                self.views.append(int((self.videoDataList[count])['statistics']['viewCount']))
            except:
                print(f"View count was not found")
                self.views.append(int(0))
                
            try:
                
                self.comment_count.append(int((self.videoDataList[count])['statistics']['commentCount']))
                
            except:
                print("comment count was not found")
                self.comment_count.append(int(0))
            

            count += 1
        
        
        
    def parseISO8601(self, duration):
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
    
    
    
    def parseVideoLength(self):
        self.seconds_list = []
        
        for i in range(len(self.video_length)):
            
            seconds = self.parseISO8601(self.video_length[i])
            self.seconds_list.append(seconds)
            self.video_length[i] = time.strftime('%H:%M:%S', time.gmtime(seconds))
    
    
    def createDF(self):
        """Create DataFrame
        """
        data = {'channelID': self.channelID,
                'channelName': self.channelName,
                'title': self.titles,
                'videoIDs':self.videoIds,
                # 'video_description': self.video_description,
                'publishedDate':self.publishedDate,
                'likes':self.like_count,
                'views':self.views,
                'comment':self.comment_count,
                'video_length':self.video_length,
                'length_in_seconds':self.seconds_list,
                'thumbnail':self.video_thumbnails}
        return pd.DataFrame(data)
        
        
        
    def downloadCSV(self):
        channelData = self.createDF()
        path = os.path.join(self.target_PATH, self.channelName)
        
        if os.path.isdir(path):
            writer = pd.ExcelWriter(f'{path}/{datetime.now().strftime("%m.%d.%Y_%H:%M")}.xlsx', engine='xlsxwriter')
            
            channelData.to_excel(writer, sheet_name = self.channelName[:30])
            writer.save()
            return channelData.to_csv(f'{path}/{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv', index=False)
            
        else:
            
            os.mkdir(path)
            writer = pd.ExcelWriter(f'{path}/{datetime.now().strftime("%m.%d.%Y_%H:%M")}.xlsx', engine='xlsxwriter')
            
            channelData.to_excel(writer, sheet_name = self.channelName[:30])
            writer.save()
            return channelData.to_csv(f'{path}/{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv', index=False)
            
        # if there is not a folder named
      
    
    