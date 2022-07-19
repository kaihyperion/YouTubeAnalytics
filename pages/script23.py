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
import plotly.graph_objects as go

def app():
    st.title("CATEGORIZATION/RETENTION PERFORMANCE ANALYSIS")
    ####################
    # initialize
    ####################
    
    
    config = configparser.ConfigParser()
    config.read('conf.ini')
    SCOPE = list(config.get('SCOPE Settings', 'scopelist').split(', '))
    auth = oauth.Authorize(scope = SCOPE, token_file= 'authentications/token.yaml', secrets_file = 'authentications/secret_ama2.json')


    auth.authorize()
    credentials = auth.get_credentials()
    
    ANALv2 = youtubeAnalytics.YouTubeAnalytics(credentials)
    DATAv3 = youtubeData.YouTubeData(credentials)
    ANALv2.api_build()
    DATAv3.api_build()
    
    
    
    #######################
    # CSV upload
    #######################
    
    if 'csv' not in st.session_state:
        ################################
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Add csv checker? so it has all the necessary column and such
        uploaded_file = st.file_uploader("CSV file here")

        if not uploaded_file:
            st.info('The CSV must contain the following columns:\n video_length (HH:MM:SS), videoIDs,content_type ')
        else:
            st.success('CSV is successfully uploaded')
            st.session_state['csv'] = pd.read_csv(uploaded_file)

            st.experimental_rerun()
            
            

            
                         
            
                
            
            
    if 'csv' in st.session_state:
        with st.form('user_options'):
            st.write("User Options to run")
            
            category_choice = st.multiselect(label = 'Choose how you would like to CATEGORIZE the data:',
                                            options=['length', 'content_type'])
            st.session_state['user_option'] = category_choice
            
            
            st.session_state['start'] = st.date_input("Start Date: ", value=datetime.strptime("2009-01-01", "%Y-%m-%d"))
            st.session_state['end'] = st.date_input("End Date: ")
            ANALv2.startDate = st.session_state['start']
            ANALv2.endDate = st.session_state['end']
            
            
            short_options = st.checkbox("Exclude Shorts")
            retention_flag = st.checkbox("Include Retention Data")
            submitted = st.form_submit_button("Submit")
        
        
        
        
        
        if submitted:
            st.success('CSV is still correctly loaded')
            ANALv2.setStartDate(st.session_state['start'])
            ANALv2.setEndDate(st.session_state['end'])
            
            # First if the short exclusion is True, get rid of shorts
            if short_options:
                st.session_state['csv'] = DATAv3.short_remover(st.session_state['csv'])
            
            
            
            col1, col2 = st.columns(2)
            if 'length' in st.session_state['user_option']:
                if 'length_in_seconds' not in st.session_state['csv']:
                    
                    #video_length_classifier will convert the session_state['csv'] to include length_category
                    st.session_state['csv'],q_array = DATAv3.video_length_classifier(st.session_state['csv'])
                    with col1:
                        st.write(st.session_state['csv']['video_length_category'].value_counts())
                    # st.write(q_array)
                    
                    with col2:
                        st.write(f"short: {int(q_array[0])} ~ {int(q_array[1])}")
                        st.write(f"medium: {int(q_array[1])} ~ {int(q_array[2])}")
                        st.write(f"long: {int(q_array[2])} ~ {int(q_array[3])}")
                else:
                    st.session_state['csv'], q_array = DATAv3.video_length_classifier(st.session_state['csv'])
                    with col1:
                        st.write(st.session_state['csv']['video_length_category'].value_counts())
                    with col2:
                        st.write(f"short: {int(q_array[0])} ~ {int(q_array[1])}")
                        st.write(f"medium: {int(q_array[1])} ~ {int(q_array[2])}")
                        st.write(f"long: {int(q_array[2])} ~ {int(q_array[3])}")

            # if 'content_type' in st.session_state['user_option']:
            # st.dataframe(st.session_state['csv'])
            #progress bar settings
            status_bar = st.progress(0)
            size = len(st.session_state['csv']['videoIDs'])
            status_current = 0
            

            
            #just debugging
            st.dataframe(st.session_state['csv'])

            
            
            
            
            
            #After the initialization, we move to next step of calling the private api
            result_final = pd.DataFrame()
            
            # Find the top 5 videos
            
            response = ANALv2.getTopNVideoIDs(metric = 'estimatedMinutesWatched',
                                              maxResults = 5)
            st.write(response)

            top5videoIDList = [i[0] for i in response['rows']]
            
            
            for video_id in st.session_state['csv']['videoIDs'].tolist():
                status_current += (1/size)
                if status_current < 1:
                    status_bar.progress(status_current)
                else:
                    status_bar.progress(100)
                
                request = ANALv2.build.reports().query(
                    endDate = ANALv2.endDate,
                    startDate = ANALv2.startDate,
                    ids = 'channel==MINE',
                    metrics = 'estimatedRevenue,cpm,subscribersGained',
                    filters = f'video=={video_id}'
                )
                response = request.execute()
                
                columns = [i['name'] for i in response['columnHeaders']]
                if response['rows'] == []:
                    # st.write('passed')
                    pass
                else:
                    df = pd.DataFrame(response['rows'])
                    df.columns = columns
                    df.insert(0, 'videoIDs', str(video_id))
                    if result_final.empty:
                        result_final = df
                    else:
                        result_final = pd.concat([result_final, df])

            
            ########################3
            # newDF: This is the dataframe that will hold all the important data that is necessary for retention analysis and CT analysis
            # use the newDF
            newDF = st.session_state['csv'].merge(result_final, on= ['videoIDs','videoIDs'])
            
            #add RPM column
            newDF = ANALv2.addRPM(newDF)
            st.dataframe(newDF)
            st.download_button("CSV download", data=newDF.to_csv().encode('utf-8'), file_name=(f'mock_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv'))
            
            # Depending on user_option, ST will display appropriate table
            if 'content_type' in st.session_state['user_option']:
                st.table(newDF.groupby('content_type')['estimatedRevenue', 'views', 'subscribersGained','RPM'].mean().style.highlight_max(color='green').highlight_min(color='pink'))
                
                # Top 5 videos from each content_type category

                content_type_list = newDF['content_type'].unique()
                content_type_top5_df = pd.DataFrame()
                for content_type in content_type_list:
                    top5 = ANALv2.getTopNVideoIDs_DF(5, newDF[newDF['content_type'] == content_type])
                    if content_type_top5_df.empty:
                        
                        content_type_top5_df = top5
                    else:
                        content_type_top5_df = pd.concat([content_type_top5_df, top5])

                st.header("This is top 5 videos of each content type")
                st.table(content_type_top5_df.groupby('content_type')['estimatedRevenue', 'views', 'subscribersGained','RPM'].mean())
                
            if 'length' in st.session_state['user_option']:
                st.dataframe(newDF.groupby('video_length_category')['estimatedRevenue', 'views', 'subscribersGained','RPM'].mean().style.highlight_max(color='green').highlight_min(color='pink'))
            
            
            
            
            
            
            ##### 
            # Retention analysis
            ##########
            
            # Retention data
            st.dataframe(newDF)
            # grab video category list video IDS
            shortVideo_ID_List = newDF.loc[newDF['video_length_category'] == 'short']['videoIDs'].tolist()
            mediumVideo_ID_List = newDF.loc[newDF['video_length_category'] == 'medium']['videoIDs'].tolist()
            longVideo_ID_List = newDF.loc[newDF['video_length_category'] == 'long']['videoIDs'].tolist()
            
            shortDF = pd.DataFrame()
            mediumDF = pd.DataFrame()
            longDF = pd.DataFrame()
            
            result_final = pd.DataFrame()
            retention_DataFrame = pd.DataFrame()
            top10 = pd.DataFrame()
            if retention_flag:
                ANALv2.setDimensions('elapsedVideoTimeRatio')
                ANALv2.setMetrics('relativeRetentionPerformance')
                for video_id in st.session_state['csv']['videoIDs'].tolist():
                    request = ANALv2.build.reports().query(
                        endDate = ANALv2.endDate,
                        startDate = ANALv2.startDate,
                        dimensions = 'elapsedVideoTimeRatio',
                        ids = 'channel==MINE',
                        metrics = 'relativeRetentionPerformance',
                        filters = 'video=='+str(video_id)
                    )
                    response = request.execute()
                    columns = [i['name'] for i in response['columnHeaders']]
                                #add a videoID column in the front
                    if response['rows'] == []:
                        # st.write("passed")
                        pass
                    else:
                        df = pd.DataFrame(response["rows"])
                        df.columns = columns
                        # df.insert(0,'videoIDs', str(video_id))
                        
                        
                        if retention_DataFrame.empty:
                            # If the overall retention Dataframe is empty, 
                            # then we just use the current dataframe and add it to the overall retention_Dataframe
                            
                            # set the overall index to elapsedVideoTimeRatio
                            # Rename the relative Retention performance column with video_id
                            df = pd.DataFrame(response["rows"])
                            df.set_index('elapsedVideoTimeRatio', inplace=True)
                            retention_DataFrame = df.rename(columns = {'relativeRetentionPerformance': video_id})
                        
                        else:
                            # if the overall retention Dataframe is not empty,
                            # then we need to merge the current response to the overall retention_Dataframe
                            retention_DataFrame = retention_DataFrame.assign(video_id = [i[1] for i in response['rows']])
                            
                            
                        # if result_final.empty:
                            
                        #     result_final = df
                        # else:
                        #     result_final = pd.concat([result_final, df])
                            
                        if video_id in shortVideo_ID_List:
                            if shortDF.empty:
                                shortDF = df
                            else:
                                shortDF = pd.concat([shortDF, df])
                        if video_id in mediumVideo_ID_List:
                            if mediumDF.empty:
                                mediumDF = df
                            else:
                                mediumDF = pd.concat([mediumDF, df])
                        if video_id in longVideo_ID_List:
                            if longDF.empty:
                                longDF = df
                            else:
                                longDF = pd.concat([longDF, df])
                            
                        if 'content_type' in st.session_state['user_option']:
                            if video_id in ANALv2.getTopNVideoIDs_DF(maxResults=10, df=newDF)['videoIDs'].tolist():
                                if top10.empty:
                                    top10 = df
                                else:
                                    top10 = pd.concat([top10, df])
                
                st.download_button("CSV download", data=result_final.to_csv().encode('utf-8'), file_name=(f'mock_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv'))

                # First get the overall relative retention performance
                a = pd.pivot_table(result_final, index = 'elapsedVideoTimeRatio', values = 'relativeRetentionPerformance', aggfunc='mean')
                total_retention_mean = a.values.mean()

                fig = px.line(a, x=a.index, y='relativeRetentionPerformance', title=str(ANALv2.channelName))
                st.plotly_chart(fig)

                st.dataframe(a)
                

                st.write("top 10")
                b = pd.pivot_table(top10, index = 'elapsedVideoTimeRatio', values = 'relativeRetentionPerformance', aggfunc='mean')


                fig = px.line(b, x=b.index, y='relativeRetentionPerformance', title=str(ANALv2.channelName))
                st.plotly_chart(fig)

                st.dataframe(b)

                st.write("percentile of top 10 videos")
                
                
                
                
                
                
                
                
                # relative retention performance BASED ON LENGTH
                st.dataframe(shortDF)
                st.header("Retention Performance: Broken Down By LENGTH")
                
                
                short = pd.pivot_table(shortDF, index = 'elapsedVideoTimeRatio', values = 'relativeRetentionPerformance', aggfunc='mean')
                try:
                    medium = pd.pivot_table(mediumDF, index = 'elapsedVideoTimeRatio', values = 'relativeRetentionPerformance', aggfunc='mean')
                except:
                    pass
                long = pd.pivot_table(longDF, index = 'elapsedVideoTimeRatio', values = 'relativeRetentionPerformance', aggfunc='mean')


 
                
                short_fig = px.line(short, x=short.index, y='relativeRetentionPerformance', title=f'Length: Short ({int(q_array[0])} ~ {int(q_array[1])}) seconds', range_y=[0,1])
      
                try:
                    medium_fig = px.line(medium, x=medium.index, y='relativeRetentionPerformance', title=f'Length: Medium ({int(q_array[1])} ~ {int(q_array[2])}) seconds', range_y=[0,1])
                except:
                    pass
                long_fig = px.line(long, x=long.index, y='relativeRetentionPerformance', title=f'Length: Long ({int(q_array[2])} ~ {int(q_array[3])}) seconds', range_y=[0,1])
                
                
                # short_f = go.Figure(data=go.Scatter(x=short.index, y = short.values, name='short'))
                # to = go.Figure(data=go.Scatter(x= a.index, y = a.values, name='total', line=dict(color='yellow')))
                # short_f.add_trace(to)
                # short_f.show()
                short_fig.data[0].line.color = "#ffa600"
                # medium_fig.data[0].line.color = '#ff6361'
                long_fig.data[0].line.color = '#bc5090'
                tab1, tab2, tab3 = st.tabs(["📈 Chart", "📊 Compare", "🗃 Data"])
                tab1.subheader("Length Category: SHORT | Retention Performance")
                tab1.plotly_chart(short_fig)
                # tab1.subheader("Length Category: Medium | Retention Performance")
                # tab1.plotly_chart(medium_fig)
                tab1.subheader("Length Category: LONG | Retention Performance")
                tab1.plotly_chart(long_fig)


  
                fig.data[0].line.color = "#58508d"
                fig.data[0].line.dash = "dash"
                fig.data[0].name = 'Total'
                

                total_fig = go.Figure(data = short_fig.data + long_fig.data + fig.data)
                total_fig.update_layout(showlegend=True)
                # f.show()
                tab2.subheader("TOTAL DATA COMPARISON ANALYSIS")
                tab2.plotly_chart(total_fig)

                
                
                col1,col2 = tab3.columns(2)
                with col1:
                    tab3.subheader("Length Category: SHORT | DataFrame")
                    tab3.dataframe(shortDF)
                # tab3.subheader("Length Category: Medium | DataFrame")
                # tab3.dataframe(mediumDF)
                with col2:
                    tab3.subheader("Length Category: LONG | DataFrame")
                    tab3.dataframe(longDF)

                # st.plotly_chart(long_fig)
                # long_fig.data[0].line.color = '#13F6E9'
                # long_f = go.Figure(data = long_fig.data + fig.data)
                # long_f.update_layout(showlegend=True)
                # st.write("Comparison to Overall")
                # st.plotly_chart(long_f)