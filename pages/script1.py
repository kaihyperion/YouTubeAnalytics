from distutils.command.upload import upload
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
import time
import string 

def app():
    st.title("script 1")
    config = configparser.ConfigParser()
    config.read('conf.ini')
    SCOPE = list(config.get('SCOPE Settings', 'scopelist').split(', '))
    auth = oauth.Authorize(scope = SCOPE, token_file= 'authentications/token.yaml', secrets_file = 'authentications/secret_ama2.json')
    

    auth.authorize()
    
    token = auth.load_token()
    credentials = auth.get_credentials()
    
    ANALv2 = youtubeAnalytics.YouTubeAnalytics(credentials)
    DATAv3 = youtubeData.YouTubeData(credentials)
    ANALv2.api_build()
    DATAv3.api_build()
    
    st.session_state['channelID'] = DATAv3.getMyChannelID()
    DATAv3.setChannelID(st.session_state['channelID'])
        
    DATAv3.getChannelRequest()
    DATAv3.getStatistics()
    
    DATAv3.getPlaylistID()
    DATAv3.getChannelName()
    
    DATAv3.setVideoList()
    DATAv3.setVideoIDList()
    
    DATAv3.setVideoDataList()
    DATAv3.videoDataParser_script1()
    DATAv3.parseVideoLength()
    
    
    #############################
    #Ask user for the date input
    
    if 'start' not in st.session_state:
        st.session_state['start'] = '2021-06-20'
    
    st.session_state['start'] = st.date_input("Start Date: ", value=datetime.strptime("2010-01-01", "%Y-%m-%d"))
    ANALv2.setStartDate(st.session_state['start'])
    
    if 'end' not in st.session_state:
        st.session_state['end'] = st.date_input("End Date: ")
        
    ANALv2.setEndDate(st.session_state['end'])
    
    date_and_gap = DATAv3.createDF_script1()
    
    date_and_gap_shorts = DATAv3.createDF_script1_shorts()
    #df holds the date and gap 
    st.write(date_and_gap)
    
    st.download_button("CSV DOWNLOAD", data=date_and_gap.to_csv().encode('utf-8'), file_name=(f'mock_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv'))

    ############################
    """Retrieving data
    Private pull for shorts, browse, suggested, search
    dimension: insightTrafficSourceType,day
    metrics: views
    channel = MINE
    
    """
    request = ANALv2.build.reports().query(
        endDate = ANALv2.endDate,
        startDate = ANALv2.startDate,
        ids = "channel==MINE",
        dimensions= 'insightTrafficSourceType,day',
        metrics = 'views'
    )
    response = request.execute()
    st.write(response)
    columns = [i['name'] for i in response['columnHeaders']]
    if response['rows'] == []:
        st.write("passed")
        pass
    else:
        df = pd.DataFrame(response["rows"])
        df.columns = columns
        

    st.dataframe(df)
    
    ####
    # Creating Day name
    day = pd.to_datetime(df['day'], format='%Y-%m-%d').dt.day_name()
    df['DOW'] = day
    cats = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    st.dataframe(df)
    df.rename(columns = {'day' : 'date'}, inplace = True)

    ### DOW AGGREAGATE
    # st.dataframe(df.groupby('DOW')['insightTrafficSourceType','day','views'].mean())
    #BROWSE category AKA('subscriber)
    browse = df[df['insightTrafficSourceType'] == "SUBSCRIBER"]
    browse['DOW'] = pd.Categorical(browse['DOW'], categories=cats, ordered=True)
    suggested = df[df['insightTrafficSourceType'] == "RELATED_VIDEO"]
    suggested['DOW'] = pd.Categorical(suggested['DOW'], categories=cats, ordered=True)
    shorts = df[df['insightTrafficSourceType'] == "SHORTS"]
    shorts['DOW'] = pd.Categorical(shorts['DOW'], categories=cats, ordered=True)
    search = df[df['insightTrafficSourceType'] == "YT_SEARCH"]
    search['DOW'] = pd.Categorical(search['DOW'], categories=cats, ordered=True)
    st.title("Days of Week Analysis on Content Types")
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col1.subheader('Browse')
    col2.subheader('Suggested')
    col3.subheader('Shorts')
    col4.subheader('Search')
    col1.dataframe(browse.groupby('DOW')['views'].mean())
    col2.dataframe(suggested.groupby('DOW')['views'].mean())
    col3.dataframe(shorts.groupby('DOW')['views'].mean())
    col4.dataframe(search.groupby('DOW')['views'].mean())
    
    
    
    
    #####
    # Posting GAPS
    # st.dataframe(df)
    # st.download_button("CSV DOWNLOAD", data=df.to_csv().encode('utf-8'), file_name=(f'mock_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv'))

    # st.dataframe(date_and_gap)
    # st.download_button("CSV DOWNLOAD2", data=date_and_gap.to_csv().encode('utf-8'), file_name=(f'mock_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv'))

    df.rename(columns = {'day' : 'date'}, inplace = True)
    df_copy = df
    df = date_and_gap.merge(df[['date', 'views', 'insightTrafficSourceType']], how='left', on='date').fillna(0)
    postingGap_browse = df[df['insightTrafficSourceType'] == 'SUBSCRIBER']
    postingGap_suggested = df[df['insightTrafficSourceType'] == 'RELATED_VIDEO']
    postingGap_shorts = df[df['insightTrafficSourceType'] == 'SHORTS']
    postingGap_search = df[df['insightTrafficSourceType'] == 'YT_SEARCH']

    st.title("Posting Gap Average analysis")
    st.write("OVERALL")
    st.dataframe(df.groupby('gap_days')['views'].mean())
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col1.subheader('Browse')
    col2.subheader('Suggested')
    col3.subheader('Shorts')
    col4.subheader('Search')
    col1.dataframe(postingGap_browse.groupby('gap_days')['views'].mean())
    col2.dataframe(postingGap_suggested.groupby('gap_days')['views'].mean())
    col3.dataframe(postingGap_shorts.groupby('gap_days')['views'].mean())
    col4.dataframe(postingGap_search.groupby('gap_days')['views'].mean())
    
    
    
    #######
    # SHORTS analysis
    df = date_and_gap_shorts.merge(df_copy[['date', 'views', 'insightTrafficSourceType']], how='left', on='date').fillna(0)
    postingGap_browse = df[df['insightTrafficSourceType'] == 'SUBSCRIBER']
    postingGap_suggested = df[df['insightTrafficSourceType'] == 'RELATED_VIDEO']
    postingGap_shorts = df[df['insightTrafficSourceType'] == 'SHORTS']
    postingGap_search = df[df['insightTrafficSourceType'] == 'YT_SEARCH']

    st.title("SHORTS Posting Gap Average analysis")
    st.write("OVERALL")
    st.dataframe(df.groupby('gap_days')['views'].mean())
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col1.subheader('Browse')
    col2.subheader('Suggested')
    col3.subheader('Shorts')
    col4.subheader('Search')
    col1.dataframe(postingGap_browse.groupby('gap_days')['views'].mean())
    col2.dataframe(postingGap_suggested.groupby('gap_days')['views'].mean())
    col3.dataframe(postingGap_shorts.groupby('gap_days')['views'].mean())
    col4.dataframe(postingGap_search.groupby('gap_days')['views'].mean())
    
    