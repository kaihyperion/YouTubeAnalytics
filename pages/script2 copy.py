from xml.dom.pulldom import PullDOM
import streamlit as st
import youtubeData
import youtubeAnalytics
import configparser
import oauth
import argparse
import pandas as pd
from datetime import datetime
import random
import string 

def app():
    st.title("TEST: Script 2")
    uploaded_file = st.file_uploader("Upload a CSV file")
    
    config = configparser.ConfigParser()
    config.read('conf.ini')
    SCOPE = list(config.get('SCOPE Settings', 'scopelist').split(', '))
    auth = oauth.Authorize(scope = SCOPE, token_file = 'authentications/token.yaml', secrets_file = 'authentications/secret_ama2.json')
    auth.authorize()
    # auth.re_authorize()
    token = auth.load_token()
    credentials = auth.get_credentials()
    
    DATAv3 = youtubeData.YouTubeData(credentials)
    ANALv2 = youtubeAnalytics.YouTubeAnalytics(credentials)
    #1) Call the api build()
    DATAv3.api_build()
    ANALv2.api_build()
    
    
    """Since we have to use private anyways, lkets grab the channelID
    """
    
    df = pd.DataFrame()
    st.session_state
    # First grab the channel ID
    st.session_state['channelID'] = DATAv3.getMyChannelID()
    DATAv3.setChannelID(st.session_state['channelID'])
    st.write(f"The channel ID is: {st.session_state['channelID']}")
    """Public Pulll
    - Video ID
    - Video Title
    - Video View Count
    - Video Length
    
    """
    """Private Pull
    - Subscribers
    - Revenue
    - RPM
    """
    """Stepos
    
    """
    
    if DATAv3.channelID != None:
        
        st.write("Running the public pull")
        DATAv3.getChannelRequest()
        # DATAv3.getStatistics()
        # st.write("Received Statistics and channel Request")
        
        st.write("Fetching playlist and video id list")
        DATAv3.getPlaylistID()
        DATAv3.getChannelName()
        
        DATAv3.setVideoList()
        DATAv3.setVideoIDList()
        
        DATAv3.setVideoDataList()
        
        DATAv3.videoDataParser()
        DATAv3.parseVideoLength()
        
        #########################################
        # df will contain the following public pulls:
        # - Video ID
        # - Video Title
        # - Video Length
        # - Views
        #######################################
        df = DATAv3.createDF_script2()
        st.write(df.shape)
        st.dataframe(df)
        random.seed(10)
        letters = string.ascii_lowercase
        random_letters = random.choices(['a','b','c','d','e','f'], k =df.shape[0])
        df = df.assign(content_type=random_letters)
        st.dataframe(df)
        st.download_button("CSV DOWNLOAD", data=df.to_csv().encode('utf-8'), file_name=(f'{DATAv3.channelName}_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv'))

        # Now run the video length anaylsis
        # the video length analysis must be divided in to short mid long
        df['video_length']
    """what we need
    Column of video id
    Video content type
    1.) Video length analysis
    - We will pull the video ids and its video length and then divide by its short mid long
    - Then assign those video length analysis to the column
    2.) Content type anaylsis
    - take list of video id and its content type/category as an input
    - So there will be column of content type/category next to video id
    3. ) private pull
    - get the private pull that will contain the followings
    - subscriber, revenue and RPM
    
    Overall goal:
    1. public pull for video id, video title, video length and views
    2. From the video length, analyze and sort and create column of video length category
    3. Add the column of content type column
    4. append private pull data
    5. with the overall dataframe, run the analysis

    """