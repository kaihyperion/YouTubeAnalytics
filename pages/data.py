import streamlit as st
import youtubeData
import configparser
import oauth
import argparse
import pandas as pd
from datetime import datetime
def app():
    st.title("YouTube Data V3 API")
    
    config = configparser.ConfigParser()
    config.read('conf.ini')
    SCOPE = list(config.get('SCOPE Settings', 'scopelist').split(', '))
    auth = oauth.Authorize(scope = SCOPE, token_file = 'authentications/token.yaml', secrets_file = 'authentications/secret_ama2.json')
    auth.authorize()
    # auth.re_authorize()
    token = auth.load_token()
    credentials = auth.get_credentials()
    
    DATAv3 = youtubeData.YouTubeData(credentials)
    #1) Call the api_build()
    DATAv3.api_build()
    
    ### Session state
    if "ChannelName" not in st.session_state and 'ChannelID' not in st.session_state:
        st.session_state['ChannelName'] = None
        st.session_state['ChannelID'] = None
    
    #### ALL streamlit inputs here
    col1, col2 = st.columns(2)
    with col1:
        inputChannelName = st.text_input("If Channel ID is unknown, ENTER Channel Name: ")
    with col2:
        inputChannelID = st.text_input("If Channel ID is known: ENTER CHANNEL ID")
    #2) if channelID is UNKNOWN
    if inputChannelName:
        st.write("Here are relevant Channel ID with corresponding Channel Name")
        relevant_ch_IDs = DATAv3.getChannelIDs(inputChannelName)
        ids = relevant_ch_IDs[0]
        desc = relevant_ch_IDs[1]
        urls = relevant_ch_IDs[2]
        idlist = []
        description = []
        u = []
        for i in range(len(ids)):
            idlist.append(ids[i])
            description.append(desc[i])
            u.append(urls[i]["url"])
        data = {'channel ID':idlist, 'description':description,'thumbnail':u}
        df = pd.DataFrame(data)
        st.dataframe(df)
        channelID = st.selectbox("select following channel ID", df)
        st.write(channelID)
        DATAv3.setChannelID(channelID)
        st.session_state['ChannelID'] = channelID
        
    elif inputChannelID:
        DATAv3.setChannelID(inputChannelID)
        st.session_state['ChannelID'] = inputChannelID
    # st.write(st.session_state)
    
    #4) Get Channel Response on statistics
    if st.session_state['ChannelID']:
        st.write("hello")
        DATAv3.getChannelRequest()
        DATAv3.getStatistics()
        
        st.write("This is Total View Count:", DATAv3.total_viewCount)
        st.write("This is Total Suybscriber Count:", DATAv3.total_subscriberCount)
        st.write("This is Total Video Count:", DATAv3.total_videoCount)
        
        DATAv3.getPlaylistID()
        DATAv3.getChannelName()
        
        DATAv3.setVideoList()
        DATAv3.setVideoIDList()
        
        DATAv3.setVideoDataList()
        DATAv3.videoDataParser()
        DATAv3.parseVideoLength()
        df = DATAv3.createDF_script2()
        st.dataframe(df)
        df = df[df['length_in_seconds'] > 90]
        st.download_button("CSV DOWNLOAD", data=df.to_csv().encode('utf-8'), file_name=(f'{DATAv3.channelName}_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv'))
