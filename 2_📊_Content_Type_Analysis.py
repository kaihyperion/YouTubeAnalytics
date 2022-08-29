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


st.title("Content Type Analysis")
# st.write(st.session_state)
config = configparser.ConfigParser()
config.read('conf.ini')
SCOPE = list(config.get('SCOPE Settings', 'scopelist').split(', '))
auth = oauth.Authorize(scope = SCOPE, token_file= 'authentications/token.yaml', secrets_file = 'authentications/secret_ama2.json')

# auth.re_authorize()
auth.authorize()

token = auth.load_token()
credentials = auth.get_credentials()

ANALv2 = youtubeAnalytics.YouTubeAnalytics(credentials)
ANALv2.api_build()



if 'data' not in st.session_state:
    
    uploaded_file = st.file_uploader("upload a CSV file")
    df = pd.read_csv(uploaded_file)
    st.session_state['data'] = df
    
    
    
    
if 'data' in st.session_state:
    st.dataframe(st.session_state['data'])
    st.write(st.session_state)
    
    # Convert HH:MM:SS -> Seconds
    st.write(st.session_state['data']['video_length'][0])
    for i in range(len(st.session_state['data']['video_length'])):
        secs = sum(int(x) * 60 ** i for i, x in enumerate(reversed(st.session_state['data']['video_length'][i].split(':'))))
        st.session_state['data']['video_length'][i] = secs
        
        
        
        
        
        
    """Video length Classification
    This will take the video length in seconds => split into 3 quantiles (short, medium, long)
    """
    
    
    # Create a video length classification
    aa = st.session_state['data']['video_length'].astype('float32')
    bb = pd.qcut(aa, 3, labels=['short', 'medium', 'long'])
    st.write(aa)
    st.write(bb)
    st.session_state['data']['video_length_category'] = bb
    st.dataframe(st.session_state['data'])

    st.write(st.session_state['data']['video_length_category'].value_counts())        
    
    
    
    
    
    #Private Pull
    
    
    if 'start' not in st.session_state:
        st.session_state['start'] = '2021-06-20'
    
    st.session_state['start'] = st.date_input("Start Date: ", value=datetime.strptime("2009-01-01", "%Y-%m-%d"))
    ANALv2.setStartDate(st.session_state['start'])
    
    st.write(ANALv2.startDate)
    
    if 'end' not in st.session_state:
        st.session_state['end'] = '2022-06-20'
        
    st.session_state['end'] = st.date_input("End Date: ")
    
    
    ANALv2.setEndDate(st.session_state['end'])
    st.write(st.session_state)
    st.write(st.session_state['data']['videoIDs'])

    result_final = pd.DataFrame()
    #Now run the private pull for revenue and cpm
    
    for video_id in st.session_state['data']['videoIDs'].tolist()[:100]:
        request = ANALv2.build.reports().query(
            endDate = ANALv2.endDate,
            startDate = ANALv2.startDate,
            ids = "channel==MINE",
            metrics = 'estimatedRevenue,cpm,subscribersGained',
            filters = f"video=={video_id}"
        )
        response = request.execute()
        columns = [i['name'] for i in response['columnHeaders']]
        if response['rows'] == []:
            st.write("passed")
            pass
        else:
            df = pd.DataFrame(response["rows"])
            df.columns = columns
            
            df.insert(0,'videoIDs', str(video_id))
            
            if result_final.empty:
                result_final = df
            else:
                result_final = pd.concat([result_final, df])
    st.dataframe(result_final)
    
    #Now attach the estimated revenue and CPM to the dataframe
    newDF=st.session_state['data'].merge(result_final, on= ['videoIDs','videoIDs'])
    st.dataframe(newDF)
    st.download_button("CSV DOWNLOAD", data=newDF.to_csv().encode('utf-8'), file_name=(f'mock_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv'))

    
    # Adding RPM 
    newDF['RPM'] = (newDF['estimatedRevenue']*1000) / (newDF['views'])
    
    ### Now Aggregate on Content Types
    st.table(newDF.groupby('content_type')['estimatedRevenue', 'views', 'subscribersGained','RPM'].mean().style.highlight_max(color='green').highlight_min(color='pink'))
    st.dataframe(newDF.groupby('video_length_category')['estimatedRevenue', 'views', 'subscribersGained','RPM'].mean().style.highlight_max(color='green').highlight_min(color='pink'))
