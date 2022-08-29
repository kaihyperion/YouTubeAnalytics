import streamlit as st
import youtubeData
import youtubeAnalytics
import configparser
import oauth
import argparse
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import time
import plotly.express as px


st.title("TEST: Retention Performance")
config = configparser.ConfigParser()
config.read('conf.ini')
SCOPE = list(config.get('SCOPE Settings', 'scopelist').split(', '))
auth = oauth.Authorize(scope = SCOPE, token_file = 'authentications/token.yaml', secrets_file = 'authentications/secret_ama2.json')
# auth.re_authorize()

auth.authorize()

token = auth.load_token()
credentials = auth.get_credentials()

DATAv3 = youtubeData.YouTubeData(credentials)
ANALv2 = youtubeAnalytics.YouTubeAnalytics(credentials)
#1) Call the api build()
DATAv3.api_build()
ANALv2.api_build()

if 'start' not in st.session_state:
    st.session_state['start'] = '2021-06-20'
    
st.session_state['start'] = st.date_input("Start Date: ")
ANALv2.setStartDate('2021-06-20')

st.write(ANALv2.startDate)

if 'end' not in st.session_state:
    st.session_state['end'] = '2022-06-20'
    
st.session_state['end'] = st.date_input("End Date: ")


ANALv2.setEndDate('2022-06-20')
st.write(ANALv2.endDate)

st.write(st.session_state)


####################
st.session_state['metrics'] = 'relativeRetentionPerformance'
st.session_state['choice'] = 'elapsedVideoTimeRatio'
ANALv2.setDimensions(st.session_state['choice'])
ANALv2.setMetrics(st.session_state['metrics'])

if st.button('next'):
    df = pd.DataFrame()
    st.session_state['channelID'] = DATAv3.getMyChannelID()
    
    DATAv3.setChannelID(st.session_state['channelID'])
    
    DATAv3.getChannelRequest()
    DATAv3.getStatistics()
    
    DATAv3.getPlaylistID()
    DATAv3.getChannelName()
    
    DATAv3.setVideoList()
    DATAv3.setVideoIDList()
    
    DATAv3.setVideoDataList()
    DATAv3.videoDataParser()
    DATAv3.parseVideoLength()
    result = DATAv3.createDF()
    
    # This is to filer out all the shorts (60 seconds and under)
    filtered_result = result.loc[result['length_in_seconds'] >60]
    
    result_final = pd.DataFrame()
    ANALv2.setChannelName(DATAv3.channelName)
    print(ANALv2.metrics)
    # st.write(filtered_result['videoIDs'].tolist()[:100])
    for i in filtered_result['videoIDs'].tolist():
        request = ANALv2.build.reports().query(
                        endDate = ANALv2.endDate,
                        startDate = ANALv2.startDate,
                        dimensions = 'elapsedVideoTimeRatio',
                        ids = "channel==MINE",
                        metrics = 'relativeRetentionPerformance',
                        filters = "video=="+str(i)
                    )
        response = request.execute()
        columns = [i['name'] for i in response['columnHeaders']]
                    #add a videoID column in the front
        if response['rows'] == []:
            st.write("passed")
            pass
        else:
            df = pd.DataFrame(response["rows"])
            df.columns = columns
            
            df.insert(0,'channelID', str(DATAv3.channelID))
            df.insert(0,'videoID', str(i))
            
            if result_final.empty:
                result_final = df
            else:
                result_final = pd.concat([result_final, df])
    # result.to_excel(writer,sheet_name=str(i)[:30])
    a = pd.pivot_table(result_final, index = 'elapsedVideoTimeRatio', values = 'relativeRetentionPerformance', aggfunc='mean')
    st.dataframe(a)
    fig = px.line(a, x=a.index, y='relativeRetentionPerformance', title=str(ANALv2.channelName))

    st.plotly_chart(fig)
