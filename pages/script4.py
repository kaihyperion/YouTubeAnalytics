from distutils.command.upload import upload
from xml.dom.pulldom import PullDOM
import streamlit as st
import youtubeData
import youtubeAnalytics
import configparser
import oauth
import argparse
import pandas as pd
from datetime import datetime, timedelta
import random
import time
import string 
import numpy as np
import altair as alt
import math
import plotly.express as px
def app():
    st.title("Script 4")
    config = configparser.ConfigParser()
    config.read('conf.ini')
    SCOPE = list(config.get('SCOPE Settings', 'scopelist').split(', '))
    auth = oauth.Authorize(scope = SCOPE, 
                           token_file= 'authentications/token.yaml',
                           secrets_file = 'authentications/secret_ama2.json')
    
    # auth.re_authorize()
    auth.authorize()
    
    token = auth.load_token()
    credentials = auth.get_credentials()
    with st.spinner('Connecting API. Please wait...'):
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
        DATAv3.videoDataParser_script4()
        DATAv3.parseVideoLength()
    st.success('API properly connected!')
    df = DATAv3.createDF_script4()
    st.dataframe(df)
    
    #Private Pull
    ANALv2.setChannelName(DATAv3.channelName)
    avg_table = pd.DataFrame()
    avg_table['days'] = range(91)[1:]
    avg_table['avg_views'] = 0.0
    total_video = len(df)
    st.write(total_video)
    
    #initialize hashtable to keep track of videos in range of 90 days
    hash_table = dict()
    for i in range(90):
        hash_table[i] = []
    
    
    status_bar = st.progress(0)
    size = len(df)
    status_current = 0
    
    
    # df holds the publishedDate and videoID.
    for index, row in df.iterrows():
        # st.write("new video")
        status_current += (1/size)
        if status_current < 1:
            status_bar.progress(status_current)
        else:
            status_bar.progress(100)
        
        # We will use strptime (to convert to datetime format)
        # we will use strftime (to convert to string)
        datetime_start = datetime.strptime(row['publishedDate'], '%Y-%m-%d')
        days90 = datetime_start + timedelta(days = 89)
        string_endDate = datetime.strftime(days90, '%Y-%m-%d')
        
        # We can potentially eliminate calling private pull if the published date is after 30/45/90/etc days before today
        today = datetime.now().date()
        today = datetime(today.year, today.month, today.day)
        day45before = today - timedelta(days=89)
        if True:
            if datetime_start < day45before:
            #Sending API request for 1 specific videoID each time
                request = ANALv2.build.reports().query(
                    startDate = row['publishedDate'],
                    endDate = string_endDate,
                    filters = f"video=={row['videoIDs']}",
                    ids="channel==MINE",
                    metrics="views",
                    dimensions="day"
                )
                
                # once response is received, we must parse it and add the appropriate views count into the hash_table
                response = request.execute()
                columns = [i['name'] for i in response['columnHeaders']]
                if response['rows'] == []:
                        pass
                else:
                    
                    video_df = pd.DataFrame(response['rows'])
                    # st.dataframe(video_df)
                    #0 is date and 1 is views
                    #sort the dataframe by date
                    video_df = video_df.sort_values(by=0)
                    # st.dataframe(video_df)
                    vidStartDate = datetime.strptime(video_df[0][0], '%Y-%m-%d')
                    #This is the date that is 'x' days from vidStartDate(publishedDate)
                    day90 = vidStartDate + timedelta(days=89)
                    vidEndDate = datetime.strptime(video_df.tail(1)[0].values[0], '%Y-%m-%d')
                    r = pd.date_range(vidStartDate, day90)
                    count = 0
                    total_days = len(video_df)
                    current = vidStartDate
                    
                    # st.write(f'video start date: {vidStartDate}')
                    # st.write(f'day90: {day90}')
                    # st.write(f'vidEndDate: {vidEndDate}')
                    #get rid of videos that don't last the whole time range
                    # st.write(r)
                    # st.write("went thru")
                    standing_total = 0

                    for date in r:
                        if current == date:
                            #if it is the first video, it should just be appended to day 0 with its view
                            if count == 0:
                                hash_table[count].append(int(video_df[1][count]))
                                standing_total += int(video_df[1][count])
                                count += 1
                                current += timedelta(days=1)
                            elif count >= total_days:
                                # if the video is cutr or deleted short of 45 days
                                hash_table[count].append(standing_total)
                                count += 1
                                current += timedelta(days=1)
                            else:
                                # if it is not the first video, then it should first aggregate from previous standing count
                                standing_total += int(video_df[1][count])
                                hash_table[count].append(standing_total)
                                count += 1
                                current += timedelta(days=1)
                                
                        elif current != date:
                            # if the current date is not equal to the range of date (meaning there is a missing date in the API pull)
                            hash_table[count].append(standing_total)    # we will just append previous standing total
                            count += 1        
                    #     if current == date:
                #         if count < total_days:
                #             hash_table[count]
                # for date in r:
                #     if current == date:
                #         if count < total_days:
                #             # st.write(video_df[1][count])
                #             hash_table[count].append(int(video_df[1][count]))
                #             current += timedelta(days=1)
                #         count += 1
                #     elif current != date and current < vidEndDate:
                #         if count < total_days:
                #             hash_table[count].append(int(0))
                #             count += 1
                #     else:
                #         print("nan was appended")
                #         hash_table[count].append(np.nan)
                #         count += 1
                # st.write(hash_table)
                # st.line_chart(list(hash_table.values()))

                # st.write(hash_table)
                # total_view = 0
                # for day, views in hash_table.items():
                #     total_view += views[0]
                #     hash_table[day].append(total_view)
                
                
            # st.write(hash_table)
            # for i in range(len(response['rows'])):
            #     # st.write(response['rows'][i][1])
            #     if i ==0:
            #         avg_table['avg_views'][i] = response['rows'][i][1]
            #     else:
            #         a = (avg_table['avg_views'][i-1]) + response['rows'][i][1]
            #         avg_table['avg_views'][i] = a
            # df = pd.DataFrame(response["rows"])
            # df.columns = columns
            
            # # df.insert(0,'videoID', str(row['videoIDs']))
            
            # if df_final.empty:
            #     df_final = df
            # else:
            #     df_final = pd.concat([df_final,df])
        
    # st.line_chart(list(hash_table.values()))
           
    #after we finish filling in the hash_table we must now do aggregate analysis
    # st.write(hash_table)
    # for day, views in hash_table.items():
    #                 total_view += views[0]
    #                 hash_table[day].append(total_view)
    #             st.line_chart(list(hash_table.values()))
    #             break
    
    # total_view += 
    # hash_table_copy = hash_table.copy()
    # total_avg = 0
    # virgin_view_total = 0
    # st.write(hash_table_copy)
    # for day, views in hash_table_copy.items():
    #     views = [x for x in views if math.isnan(x) == False]
    #     virgin_view_total += np.sum(views)
    #     total_avg += virgin_view_total/len(views)
    #     hash_table_copy[day] = virgin_view_total
    # st.write(list(hash_table_copy.values()))
    # st.line_chart(list(hash_table_copy.values()))
    st.write(hash_table)
    x = []
    y = []
    newdf = pd.DataFrame.from_dict(hash_table, orient='index').transpose()
    st.dataframe(newdf)
    for key in hash_table.keys():
        for value in hash_table[key]:
            x.append(key+1)
            y.append(value)
    fig = px.scatter(x=x, y=y, trendline="ols", trendline_options=dict(log_x=True), title='OLS trendline with log transformation of x')
    fig.update_traces(visible=False, selector=dict(mode="markers"))
    fig.show()
    st.plotly_chart(fig)
    st.write(f'x is: {hash_table.keys}')
    hash_table_copy = hash_table.copy()
    for day, views in hash_table_copy.items():
        # hash_table_copy[day] = np.mean(views)
        hash_table_copy[day] = np.sum(views)/total_video
    st.write(hash_table_copy)
    st.line_chart(list(hash_table.values()))
    st.line_chart(list(hash_table_copy.values()))
    
    st.balloons()
    ############################################
    # total_view = 0
    # for day, views in hash_table_copy.items():
    #     views = [x for x in views if math.isnan(x) == False]
    #     total_view += np.sum(views)
    #     ss = len(views)
    #     hash_table_copy[day] = total_view
    # status_bar.progress(100)
    ############################################
    
    # c = alt.Chart(list(hash_table_copy.values())).mark_line()
 
    # st.altair_chart(c)
    # avg_table['avg_views']/total_video
    # st.dataframe(avg_table)
    # st.line_chart(avg_table['avg_views'].to_list())
    # st.dataframe(df_final)
    # st.download_button("CSV DOWNLOAD", data=df_final.to_csv().encode('utf-8'), file_name=('script4data.csv'))

    
    
                
    