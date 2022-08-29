from cmath import nan
import os
import argparse
import time
import configparser
from googleapiclient.discovery import build
from numpy import datetime64
import generate_conf
import re
import pandas as pd
import numpy as np
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
        print(response)
        self.total_viewCount = response['viewCount']
        # self.total_subscriberCount = response['subscriberCount']
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
            
            tmp = self.build.videos().list(id= ','.join(self.videoIDList[i:i+40]), part= 'statistics, contentDetails, status').execute()
            info_video += tmp['items']
            
        self.videoDataList = info_video
        print(self.videoDataList)
        
        
        
    
    def videoDataParser(self):
        #!!! i dont know why the videoIDList is 1 number higher than videodatalist...
        for count in range(0, len(self.videoIDList)-1):
            
            
            if self.videoDataList[count]['status']['privacyStatus'] == 'public':
                self.titles.append((self.videoList[count])['snippet']['title'])
                self.publishedDate.append((self.videoList[count])['snippet']['publishedAt'])
                self.video_description.append((self.videoList[count])['snippet']['description'])
                self.videoIds.append(self.videoList[count]['snippet']['resourceId']['videoId'])
                try:
                    self.video_thumbnails.append(self.videoList[count]['snippet']['thumbnails']['default']['url'])
                except:
                    self.video_thumbnails.append('')
                try:
                    self.video_length.append(self.videoDataList[count]['contentDetails']['duration'])
                except:
                    print(f"video length was not found")
                    self.video_length.append(int(0))
                try:
                    self.like_count.append(int((self.videoDataList[count])['statistics']['likeCount']))
                except:
                    print(f"Like count was not found")
                    self.like_count.append(int(0))
                try:
                    self.dislike_count.append(int((self.videoDataList[count])['statistics']['dislikeCount']))
                except:
                    # print(f"Dislike count was not found")
                    
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
    def videoDataParser_script1(self):
        for count in range(0, len(self.videoIDList)):
            self.titles.append((self.videoList[count])['snippet']['title'])
            # print((self.videoList[count])['snippet']['publishedAt'])
            self.publishedDate.append((self.videoList[count])['snippet']['publishedAt'])
            self.videoIds.append(self.videoList[count]['snippet']['resourceId']['videoId'])
            try:
                self.video_length.append(self.videoDataList[count]['contentDetails']['duration'])
            except:
                print(f"video length was not found")
                self.video_length.append(int(0))
            

            count += 1


    ### !!! This is possible that we might remove 1+ video that is not a short due to the fact that video length was not found
    def videoDataParser_script4(self):
        for count in range(0, len(self.videoIDList)):
            # self.titles.append((self.videoList[count])['snippet']['title'])
            # print((self.videoList[count])['snippet']['publishedAt'])
            self.publishedDate.append(((self.videoList[count])['snippet']['publishedAt']).split('T')[0])
            self.videoIds.append(self.videoList[count]['snippet']['resourceId']['videoId'])
            try:
                self.video_length.append(self.videoDataList[count]['contentDetails']['duration'])
            except:
                print(f"video length was not found")
                self.video_length.append(int(0))
            

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
                'length_in_seconds':self.seconds_list
                # 'thumbnail':self.video_thumbnails
                }
        return pd.DataFrame(data)
    
    
    def createDF_script4(self):
        data = {'publishedDate': self.publishedDate,
                'videoIDs': self.videoIds,
                'length_in_seconds':self.seconds_list
                }
        df = pd.DataFrame(data)
        df = df[df['length_in_seconds'] > 60]
        
        return df
    def createDF_script2(self):
        data = {'videoIDs': self.videoIds,
                'videoTitle': self.titles,
                'video_length': self.video_length,
                'length_in_seconds':self.seconds_list,
                'publishedDate': self.publishedDate,
                'views': self.views,
                'thumbnail': self.video_thumbnails
                }
        return pd.DataFrame(data)
        
    
    
    def gap_calculator(self, df):
        count = 0
        # print("gap calculator")
        for i in range(len(df['gap'])):
            if df['gap'][i] == False:
                df['gap'][i] = count
                if i+1 < len(df['gap']):
                    if df['date'][i+1] == df['date'][i]:
                        pass
                    else:
                        count = 0
            else:
                count += 1
        
        return df
    
    def gap_calculator2(self, df):
        df['gap_days'] = 0
        count = 0
        for i in range(len(df['gap'])):
            if df['gap'][i] == False:
                df['gap_days'][i] = 0
                count = 0
            else:
                count += 1
                df['gap_days'][i] = count
        return df
    
    
    def createDF_script1_shorts(self):
        data = {
            'publishedDate': self.publishedDate,
            'length_in_seconds':self.seconds_list
            }
        df = pd.DataFrame(data)
        
        # first get rid of shorts
        df = df.loc[df['length_in_seconds'] <= 60]
        dates = [i.split('T')[0] for i in df['publishedDate'].to_list()]
        timestamps = [pd.Timestamp(i) for i in dates]
        gaps = [int(0) for i in range(len(timestamps))]
        series = pd.Series(gaps, index=timestamps)
        s = pd.Series(index=pd.date_range(series.index.min(), 
                                          series.index.max(), 
                                          freq='D').difference(series.index))
        s= s.fillna(1.0)
        result = pd.concat([series, s]).sort_index()
        # print("sorting complete")
        result = result.fillna(False)
        result = result.astype(bool)
        final = pd.DataFrame({'date':result.index, 'gap':result.values})
        # print("created dataframe")
        # final = result.to_frame()
        # final = final.rename(columns = {0:'item'})
        # # final = result.astype(bool)
        # # final = pd.DataFrame(result.astype(bool))
        # print(type(final))
        # print(f"This is column names: {final.columns}")
        really_final = self.gap_calculator2(final)
        # print(really_final.columns)
        return really_final.astype(str)
    
    
    def createDF_script1(self):
        data = {
                'publishedDate': self.publishedDate,
                'length_in_seconds':self.seconds_list
                }
        df = pd.DataFrame(data)
        
        # first get rid of shorts
        df = df.loc[df['length_in_seconds'] > 60]
        dates = [i.split('T')[0] for i in df['publishedDate'].to_list()]
        timestamps = [pd.Timestamp(i) for i in dates]
        gaps = [int(0) for i in range(len(timestamps))]
        series = pd.Series(gaps, index=timestamps)
        s = pd.Series(index=pd.date_range(series.index.min(),
                                          series.index.max(), 
                                          freq='D').difference(series.index))
        s= s.fillna(1.0)
        result = pd.concat([series, s]).sort_index()
        # print("sorting complete")
        result = result.fillna(False)
        result = result.astype(bool)
        final = pd.DataFrame({'date':result.index, 'gap':result.values})
        # print("created dataframe")
        # final = result.to_frame()
        # final = final.rename(columns = {0:'item'})
        # # final = result.astype(bool)
        # # final = pd.DataFrame(result.astype(bool))
        # print(type(final))
        # print(f"This is column names: {final.columns}")
        really_final = self.gap_calculator2(final)
        # print(really_final.columns)
        return really_final.astype(str)
        return pd.DataFrame(pd.concat([series, s]).sort_index())
        df2 = pd.DataFrame()
        
        
        return df
        # df['publishedDate']= pd.to_datetime(df['publishedDate'])

        print(pd.to_datetime(df['publishedDate'].min()).strftime('%Y-%m-%d'))
        # print(df['publishedDate'].min().astype(datetime64))
        r = pd.date_range(start=pd.to_datetime(df['publishedDate'].min()).strftime('%Y-%m-%d'), end=pd.to_datetime(df['publishedDate'].max()).strftime('%Y-%m-%d'))
        print(r.strftime('%Y-%m-%d'))
        print(df['publishedDate'])
        r = r.strftime('%Y-%m-%d')
        # return df.set_index('publishedDate').reindex(r).fillna(0.0).rename_axis('publishedDates').reset_index()
        # idx = pd.period_range(start=df['publishedDate'].min(), end=df['publishedDate'].max())
        # return df.reindex(r).fillna(0).rename_axis('publishedDates').reset_index()
        print(pd.DatetimeIndex(df['publishedDate']))
        return df.set_index(pd.DatetimeIndex(df['publishedDate']))
        # return df.reindex(r, fill_value=0)
        # df.index = pd.DatetimeIndex(df.index)
        # df = df.reindex(pd.date_range('09-01-2020','09-01-2018'), fill_value=0)
        # df['publishedDate'] = pd.to_datetime(df['publishedDate'], format = '%Y-%m-%d')
        # df = df.sort_values(by='publishedDate')
        # df.set_index('publishedDate', inplace=True)
        # df = df.resample('D').ffill().reset_index()
        
    
    
        
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
      
    
    def TTS_converter(self,df):
        # Time (HH:MM:SS) to Seconds (s) converter
        
        
        for i in range(len(df['video_length'])):
            
            secs = sum(int(x) * 60 ** i for i, x in enumerate(reversed(df['video_length'][i].split(':'))))
            df.loc[i, 'length_in_seconds'] = secs

        return df
    
    ####
    # Short Remover:
    # This removes all the shorts
    def short_remover(self,df):
        # there must be a column with seconds (called video_length)
        if 'length_in_seconds' in df:
            filtered_result = df.loc[df['length_in_seconds'] > 60].reset_index(drop=True)
            
        else:
            df = self.TTS_converter(df)
            filtered_result = df.loc[df['length_in_seconds'] > 60].reset_index(drop=True)
            
            
        return filtered_result



    def video_length_classifier(self, df):
        
        # First time to seconds convert
        df = self.TTS_converter(df) 
        
        q_array = pd.qcut(df['length_in_seconds'].astype('int'), 
                                  3, retbins=True)
        #takes in dataframe of public pull and classify into 3 quantiles
        length_category = pd.qcut(df['length_in_seconds'].astype('int'), 
                                  3, 
                                  labels=['short', 'medium', 'long'])
        
        # add the appropriate length category into the original DataFrame
        df['video_length_category'] = length_category
        
        return df, q_array[1]
        