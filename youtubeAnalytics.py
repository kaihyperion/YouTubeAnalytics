import os
import argparse
import time
import configparser
from argon2 import PasswordHasher
from googleapiclient.discovery import build
import generate_conf
import re
import numpy as np
from datetime import datetime
import streamlit as st
class YouTubeAnalytics:
    """
    YouTube Analytics API
    API request contains FIVE (5) parameters
    1.) startDate and endDate - specify the time period for which the report will contain data
    2.) metrics - specifies the measurements that will be included in the report. 
                    this includes user activity and values such as 'likes and views, etc'
    3.) dimensions - determines how the metrics will be GROUPED
    4.) filters - explains how the report data will be filtered. rather than returning all
                of the data for a channel, a report could be filtered to only contain metrics for a certain country, video, or group of videos.
    
    """
    # pull the videoIdList using YouTubeData!!!!!!
    def __init__(self, credentials):
        config = configparser.ConfigParser()
        config.read('conf.ini')
        
        ### Configuration Settings
        self.api_name = config.get('YouTube Analytics', 'api_service_name')
        self.api_version = config.get('YouTube Analytics', 'api_version')
        self.credentials = credentials
        
        self.api_key = config.get('YouTube Data', 'api_key')
        self.build = None
        
        
        ### Analytics API Request API Query Parameters
        self.current_PATH = os.path.dirname(os.path.abspath(__file__))
        self.target_PATH = os.path.join(self.current_PATH, 'anal')
        # i.e. 2015-06-01
        self.startDate = None
        self.endDate = None
        
        # ageGroup, channel, country, day, gender, month, sharingService, uploaderType, video, 7DayTotals, 30DayTotals
        self.dimensions = None
        
        #metrics
        # annotationClickThroughRate, annotiationCloseRate, averageViewDuration, comments, dislikes, estimatedMinutesWatched, estimatedRevenue, likes, shares, subscribersGained, subscribersLost, viewerPercentage, views
        self.metrics = None
        
        #filters
        self.filters = None
        
        self.videoIDList = None
        
        self.ids = "channel==MINE"
        
        self.channelName = None
        
    def api_build(self):
        self.build = build(serviceName = self.api_name, version = self.api_version, credentials = self.credentials)
    
    
    def setVideoIDList(self, IDList):
        self.videoIDList = IDList
        
        
    def setStartDate(self, date):
        self.startDate = date
        
        
    def setEndDate(self, date):
        self.endDate = date
    
    
    def setDimensions(self, dimension):
        self.dimensions = dimension
        
        
    def setMetrics(self, metric):
        self.metrics = ",".join(metric)
    
        
    def setChannelName(self, name):
        self.channelName = name
    def setFilter(self, filter):
        self.filters = filter
    
    def setIds(self, ids):
        self.ids = ids
    
    def addRPM(self, df):
        temp = df.copy()
        st.dataframe(temp)
        temp['RPM'] = (temp['estimatedRevenue'] * 1000 / (temp['views']))
        temp['RPM'][np.isinf(temp['RPM'])] = 0
        st.dataframe(temp)
        return temp
    
    def downloadCSV(self, channelData, videoid):
        path = os.path.join(self.target_PATH, self.channelName)
        if os.path.isdir(path):
            return channelData.to_csv(f'{path}/{videoid}_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv', index=False)
        else:
            os.mkdir(path)
            return channelData.to_csv(f'{path}/{videoid}_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv', index=False)
       
    def getTopNVideoIDs(self,maxResults=5, metric=''):
        
        request = self.build.reports().query(
            endDate = self.endDate,
            startDate = self.startDate,
            metrics = 'estimatedMinutesWatched',
            ids = 'channel==MINE',
            maxResults = maxResults,
            sort = f'-{metric}',
            dimensions = 'video'
        )
        response = request.execute()
        
            
        return response
    
    def getTopNVideoIDs_DF(self, maxResults, df):
        videoIDList=df.sort_values(by='views', ascending=False)[:maxResults]
        return videoIDList