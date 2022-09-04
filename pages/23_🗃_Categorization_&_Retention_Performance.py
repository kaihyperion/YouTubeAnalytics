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
import timeit



##################################################
# Categorization/Retention Performance Analysis #
##################################################



# st.set_page_config(page_title="Plotting Demo", page_icon="📈")
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
        data = pd.read_csv(uploaded_file, index_col=0)
        data = data.drop_duplicates(subset=['videoIDs'], keep='first', ignore_index=True)
        st.session_state['csv'] = data
        st.dataframe(st.session_state['csv'])
        # st.stop()
        st.experimental_rerun()
        
        

        
        
        
if 'csv' in st.session_state:
    with st.form('user_options'):
        
        
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
        
        # Find the Length Category of videos
        
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

        if 'content_type' in st.session_state['user_option']:
            s = st.session_state['csv']['content_type']
            count = s.value_counts()
            percent = s.value_counts(normalize=True).mul(100).round(1).astype(str) + '%'
            st.subheader('Content Type Video Count')
            st.table(pd.DataFrame({'Video Count': count, 'Percent': percent}).sort_index())
            # st.session_state['csv']['content_type'].index.name = 'content_type'
            # st.table(st.session_state['csv']['content_type'].value_counts().sort_index().rename('Video Count'))  


        #just debugging
        csv_expander = st.expander("Click Here to see the uploaded CSV file")
        csv_expander.dataframe(st.session_state['csv'])
        # st.dataframe(st.session_state['csv'])
        
        
        # if 'content_type' in st.session_state['user_option']:
        # st.dataframe(st.session_state['csv'])
        #progress bar settings
        status_bar = st.progress(0)
        size = len(st.session_state['csv']['videoIDs'])
        status_current = 0
        

        
        

        
        
        
        
        
        #After the initialization, we move to next step of calling the private api
        
        result_final = pd.DataFrame()
        
        # Find the top 5 videos
        
        response = ANALv2.getTopNVideoIDs(metric = 'estimatedMinutesWatched',
                                            maxResults = 5)
        # st.write(response)

        top5videoIDList = [i[0] for i in response['rows']]
        
        # token_expiry = st.session_state['user_token']['expires_at']
        # token_expiry_datetime = datetime.fromtimestamp(token_expiry)
        
        
        
        ################## temp ###############################
        startTime = time.time()
        temp_list = st.session_state['csv']['videoIDs'].tolist()[:499]
        # st.write(temp_list)
        # st.subheader("request making")
        request = ANALv2.build.reports().query(
            dimensions = 'video',
            endDate = ANALv2.endDate,
            startDate = ANALv2.startDate,
            ids = 'channel==MINE',
            metrics = 'estimatedRevenue,cpm,subscribersGained',
            filters = f'video=={",".join(temp_list)}'
        )
        # st.subheader("request made | calling api")
        response = request.execute()
        
        a = pd.json_normalize(response, 'rows')
        
        if a.empty:
            st.write("No data found")
            st.stop()
        
        st.write(f"time taken: {time.time() - startTime}")
        
        
        a.columns = [i['name'] for i in response['columnHeaders']]
        # st.write(f"columns are {columns}")
        st.dataframe(a)
        
        # a.columns = columns
        result_final =a
        # st.dataframe(a)
        ################## temp ###############################
        
        
        # startTime = time.time()
        # for video_id in st.session_state['csv']['videoIDs'].tolist()[:499]:
            
        #     # if datetime.now() < token_expiry_datetime:
        #     #     auth.token_Refresh()
        #     #     # update the token_expiry_Datetime
                
        #     status_current += (1/size)
        #     if status_current < 1:
        #         status_bar.progress(status_current)
        #     else:
        #         status_bar.progress(100)
            
        #     request = ANALv2.build.reports().query(
        #         endDate = ANALv2.endDate,
        #         startDate = ANALv2.startDate,
        #         ids = 'channel==MINE',
        #         metrics = 'estimatedRevenue,cpm,subscribersGained',
        #         filters = f'video=={video_id}'
        #     )
        #     response = request.execute()
            
        #     columns = [i['name'] for i in response['columnHeaders']]
        #     if response['rows'] == []:
        #         # st.write('passed')
        #         pass
        #     else:
        #         df = pd.DataFrame(response['rows'])
        #         df.columns = columns
        #         df.insert(0, 'videoIDs', str(video_id))
        #         if result_final.empty:
        #             result_final = df
        #         else:
        #             result_final = pd.concat([result_final, df])
        # st.write(f"time taken: {time.time() - startTime}")
        # st.dataframe(result_final)
        ########################3
        # newDF: This is the dataframe that will hold all the important data that is necessary for retention analysis and CT analysis
        # use the newDF
        # st.dataframe(st.session_state['csv'])
        result_final=result_final.rename(columns = {'video':'videoIDs'})
        newDF = result_final.merge(st.session_state['csv'], on= ['videoIDs','videoIDs'])
        # newDF = pd.merge(st.session_state['csv'], result_final, on)
        #add RPM column
        st.dataframe(newDF)
        newDF = ANALv2.addRPM(newDF)
        
        finalDF_expander = st.expander("Click Here to see the final dataframe and to download the CSV")
        finalDF_expander.dataframe(newDF)
        
        # st.dataframe(newDF)
        finalDF_expander.download_button("CSV download", data=newDF.to_csv().encode('utf-8'), file_name=(f'mock_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv'))
        
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
        # st.dataframe(newDF)
        # grab video category list video IDS
        shortVideo_ID_List = newDF.loc[newDF['video_length_category'] == 'short']['videoIDs'].tolist()
        mediumVideo_ID_List = newDF.loc[newDF['video_length_category'] == 'medium']['videoIDs'].tolist()
        longVideo_ID_List = newDF.loc[newDF['video_length_category'] == 'long']['videoIDs'].tolist()
        
        
        
        shortDF = pd.DataFrame()
        mediumDF = pd.DataFrame()
        longDF = pd.DataFrame()
        
        
        
        result_final = pd.DataFrame()
        retention_DataFrame = pd.DataFrame(np.arange(0.01, 1.01, 0.01),
                                            columns= ['ratio'])
        # retention_DataFrame = retention_DataFrame.set_index('elapsedVideoTimeRatio')
        top10 = pd.DataFrame()
        
        
        if retention_flag:
            ANALv2.setDimensions('elapsedVideoTimeRatio')
            ANALv2.setMetrics('relativeRetentionPerformance')
            for video_id in st.session_state['csv']['videoIDs'].tolist():
                
                st.write("Retention Requested")
                start = timeit.default_timer()
                overall_start = timeit.default_timer()
                
                request = ANALv2.build.reports().query(
                    endDate = ANALv2.endDate,
                    startDate = ANALv2.startDate,
                    dimensions = 'elapsedVideoTimeRatio',
                    ids = 'channel==MINE',
                    metrics = 'relativeRetentionPerformance',
                    filters = 'video=='+str(video_id)
                )
                response = request.execute()
                st.write('Time took was :', timeit.default_timer() - start)
                st.write('After request dataframe management')
                start = timeit.default_timer()
                
                
                
                
                
                
                # st.write(video_id)
                
                df = pd.json_normalize(response, 'rows')
                try:
                    df.columns = ['elapsedVideoTimeRatio', str(video_id)]
                    # a=a.set_index('elapsedVideoTimeRatio', inplace=True)
                    # a.set_index('elapsedVideoTimeRatio', inplace=True)
                    # st.dataframe(a)
                    # st.subheader("adding")
                    retention_DataFrame = pd.concat([retention_DataFrame, df[video_id]], axis=1)
                except:
                    st.write(f"Video ID {video_id} has no data. We will skip")
                    pass
                # st.dataframe(retention_DataFrame)
                
                # columns = [i['name'] for i in response['columnHeaders']]
                            #add a videoID column in the front
                # if response['rows'] == []:
                #     st.write("passed")
                #     pass
                # else:
                #     df = pd.DataFrame(response["rows"])
                #     df.columns = columns
                #     # df.insert(0,'videoIDs', str(video_id))
                    
                    
                #     if retention_DataFrame.empty:
                #         # If the overall retention Dataframe is empty, 
                #         # then we just use the current dataframe and add it to the overall retention_Dataframe
                        
                #         # set the overall index to elapsedVideoTimeRatio
                #         # Rename the relative Retention performance column with video_id
                #         df = pd.DataFrame(response["rows"], columns=['elapsedVideoTimeRatio', 'relativeRetentionPerformance'])
                #         df.set_index('elapsedVideoTimeRatio', inplace=True)
                #         # df.index.name = 'index_column'
                        
                        
                #         df.rename(columns={'relativeRetentionPerformance': str(video_id)}, inplace=True)
                #         retention_DataFrame = df
                #         st.write("empty | initialized!")
                        

                #     else:
                #         # if the overall retention Dataframe is not empty,
                #         # then we need to merge the current response to the overall retention_Dataframe
                #         try:
                #             retention_DataFrame.insert(loc=len(retention_DataFrame.columns), column = str(video_id), value = [i[1] for i in response['rows']])
                            

                #         except:
                #             st.write("FAIL")
                #             st.write(response['rows'])
                #             st.dataframe(retention_DataFrame)
                        
                        
                #     # if result_final.empty:
                        
                #     #     result_final = df
                #     # else:
                #     #     result_final = pd.concat([result_final, df])
                    
                    
                    
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
                st.write("It took :", timeit.default_timer() - start)
            
            
            
            # once the Retention data is collected, we can display by LENGTH CATEGORY
            # We have short, medium and long video id list
            # short: shortVideo_ID_List
            # mid: mediumVideo_ID_List
            # long: longVideo_ID_List
            # retention_DataFrame: retention_DataFrame
            
            # st.dataframe(retention_DataFrame)
            retentionDF_expander = st.expander("Retention DataFrame | Expand to see DataFrame and download CSV")
            retentionDF_expander.dataframe(retention_DataFrame)
            
            
            ### Display by Content Type
            # content_type_list has all the content types
            # we need to grab all the video ids of that corresponding content types
            temp_df = pd.DataFrame()
            temp_hash = dict()
            content_type_length = len(content_type_list)
            
            for content_type in sorted(content_type_list):
                video_idlist = newDF.loc[newDF['content_type'] == content_type]['videoIDs'].tolist()
                
                temp_hash[content_type] = video_idlist
                
                
            with st.expander("Retention DataFrame by Content Type | Expand to see DataFrame and download CSV"):
                for content_type in sorted(content_type_list):
                    video_idlist = temp_hash[content_type]
                    
                    content_type_mu_elapsedVideoTimeRatio = retention_DataFrame[video_idlist].mean(axis = 1)
                    
                    st.subheader(content_type)
                    fig = px.line(content_type_mu_elapsedVideoTimeRatio,
                                labels={'elapsedVideoTimeRatio': 'Elapsed Video Time Ratio', 'value':'Retention Performance'},
                                title = 'Retention Performance by Content Type: '+content_type)
                    st.plotly_chart(fig)
            
            # st.write(temp_hash)
            # for content_type in sorted(a):
            #     retention_DataFrame[a[content_type]].mean(axis = 1)
            #     CT_fig = px.line(retention_DataFrame[a[content_type]].mean(axis = 1))
            # short = retention_DataFrame[shortVideo_ID_List]
            # mid = retention_DataFrame[mediumVideo_ID_List]
            # long = retention_DataFrame[longVideo_ID_List]
            # axis = 1 will give us the average of each row. (total of 100 rows)
            # axis = 0 will give us the average of each column. (total number of data = total number of videos)
            overall_mu = retention_DataFrame.mean().mean()
            
            short_mu_elapsedVideoTimeRatio = retention_DataFrame[shortVideo_ID_List].mean(axis = 1)
            short_mu_video = retention_DataFrame[shortVideo_ID_List].mean(axis = 0)
            mid_mu_elapsedVideoTimeRatio = retention_DataFrame[mediumVideo_ID_List].mean(axis = 1)
            mid_mu_video = retention_DataFrame[mediumVideo_ID_List].mean(axis = 0)
            long_mu_elapsedVideoTimeRatio = retention_DataFrame[longVideo_ID_List].mean(axis = 1)
            long_mu_video = retention_DataFrame[longVideo_ID_List].mean(axis = 0)
            
            # We need to show the following:
            # 1. The average of the retention performance for each video length category
            # 2. The average of the retention performance for each content type category
            # 3. aggreaget graph of entire retnetion performance
            # 4. Table showing the top 10 videos with the highest retention performance (mean of the entire dataframe and find top 10)
            
            # Retention performance for each video length category (short, medium, long)
            # We need to use axis = 1 to get the average of each row i.e. [____mu_video variables]
            # short_fig = px.line(short_mu_elapsedVideoTimeRatio, x='elapsedVideoTimeRatio', y='relativeRetentionPerformance', title='Retention performance [SHORT]')
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Overall", "📊 Short", "🗃 Medium", "🗃 Long"])
            retention_fig = px.line(short_mu_elapsedVideoTimeRatio, 
                                labels={'elapsedVideoTimeRatio': 'Elapsed Video Time Ratio', 'value':'Retention Performance'},
                                title = 'Retention Performance by Length Category')
            
            
            retention_fig.data[0].update(
                name = 'Short',
                line = {'color':"#00E94F", 'dash':'solid'}
            )
            short_fig = go.Figure(retention_fig)
            short_fig.data[0].update(
                name = 'Short',
                line = {'color':"#00E94F", 'dash':'solid'}
            )
            
            medium_fig = px.line(mid_mu_elapsedVideoTimeRatio,
                                labels={'elapsedVideoTimeRatio': 'Elapsed Video Time Ratio', 'value':'Retention Performance'},
                                title = 'Retention Performance by Length Category')
            medium_fig.data[0].update(
                name = 'Medium',
                line = {'color':'#00C0A3', 'dash':'solid'}
                
            )

            long_fig = px.line(long_mu_elapsedVideoTimeRatio,
                                labels={'elapsedVideoTimeRatio': 'Elapsed Video Time Ratio', 'value':'Retention Performance'},
                                title='Retention Performance by Length Category')
            long_fig.data[0].update(
                name = 'Long',
                line = {'color':'#3d90FC', 'dash':'solid'}
                
            )
            
            total_fig = px.line(retention_DataFrame.mean(axis=1),
                                labels={'elapsedVideoTimeRatio': 'Elapsed Video Time Ratio', 'value':'Retention Performance'},
                                title='Retention Performance by Length Category')
            total_fig.data[0].update(
                name = 'Total',
                line = {'color':'#DF8AF4', 'dash':'dash'}
            )
            retention_fig.add_traces(data = medium_fig.data + long_fig.data + total_fig.data)
            
            tab1.subheader('Retention Performance by Length Category | OVERALL')
            tab1.plotly_chart(retention_fig)
            tab1.write("Average Retention Performance by Length Category compared to Overall Average of the channel:")
            retention_col1, retention_col2, retention_col3 = tab1.columns(3)
            retention_col1.metric("Short", str(round(short_mu_video.mean(),4)), str(round((short_mu_video.mean() - overall_mu),4)))
            retention_col2.metric("Medium", str(round(mid_mu_video.mean(),4)), str(round((mid_mu_video.mean()-overall_mu),4)))
            retention_col3.metric("Long", str(round(long_mu_video.mean(),4)), str(round((long_mu_video.mean() - overall_mu),4)))
            
            
            
            
            
            tab2.subheader('Retention Performance by Length Category | SHORT')
            short_top5 = short_mu_video.sort_values(ascending=False).head(5)
            tab2.plotly_chart(short_fig.add_traces(data= total_fig.data))
            tab2_col1, tab2_col2 = tab2.columns([1,5])
            tab2_col1.metric("Average", str(round(short_mu_video.mean(),4)), str(round((short_mu_video.mean() - overall_mu),4)), help = "Average Retention Performance by Short Video Length compared to Overall Average of the channel")
            tab2_col2.dataframe(newDF[newDF['videoIDs'].isin(short_top5.index.tolist())])
            
            tab2.subheader("Top 5 Short Videos:")
            top1_short, top2_short, top3_short, top4_short, top5_short = tab2.columns(5)
            top1_short.metric(f"Top 1: {short_top5.index[0]}", round(short_top5[0],4) , round((short_top5[0] - short_mu_video.mean()),4))
            top1_short.write(f"[{short_top5.index[0]}](https://www.youtube.com/watch?v={short_top5.index[0]})")
            top2_short.metric(f"Top 2: {short_top5.index[1]}", round(short_top5[1],4) , round((short_top5[1] - short_mu_video.mean()),4))
            top2_short.write(f"[{short_top5.index[1]}](https://www.youtube.com/watch?v={short_top5.index[1]})")
            top3_short.metric(f"Top 3: {short_top5.index[2]}", round(short_top5[2],4) , round((short_top5[2] - short_mu_video.mean()),4))
            top3_short.write(f"[{short_top5.index[2]}](https://www.youtube.com/watch?v={short_top5.index[2]})")
            top4_short.metric(f"Top 4: {short_top5.index[3]}", round(short_top5[3],4) , round((short_top5[3] - short_mu_video.mean()),4))
            top4_short.write(f"[{short_top5.index[3]}](https://www.youtube.com/watch?v={short_top5.index[3]})")
            top5_short.metric(f"Top 5: {short_top5.index[4]}", round(short_top5[4],4) , round((short_top5[4] - short_mu_video.mean()),4))
            top5_short.write(f"[{short_top5.index[4]}](https://www.youtube.com/watch?v={short_top5.index[4]})")
            
            
            
            
            tab3.subheader('Retention Performance by Length Category | MEDIUM')
            medium_top5 = mid_mu_video.sort_values(ascending=False).head(5)
            medium_fig.data[0].update(
                
            )
            tab3.plotly_chart(medium_fig.add_traces(data= total_fig.data))
            tab3_col1, tab3_col2 = tab3.columns([1,5])
            tab3_col1.metric("Average", str(round(mid_mu_video.mean(),4)), str(round((mid_mu_video.mean() - overall_mu),4)), help = "Average Retention Performance by Medium Video Length compared to Overall Average of the channel")
            tab3_col2.dataframe(newDF[newDF['videoIDs'].isin(medium_top5.index.tolist())])
            
            tab3.subheader("Top 5 Medium Videos:")
            top1_medium, top2_medium, top3_medium, top4_medium, top5_medium = tab3.columns(5)
            top1_medium.metric(f"Top 1: {medium_top5.index[0]}", round(medium_top5[0],4) , round((medium_top5[0] - mid_mu_video.mean()),4))
            top1_medium.write(f"[{medium_top5.index[0]}](https://www.youtube.com/watch?v={medium_top5.index[0]})")
            top2_medium.metric(f"Top 2: {medium_top5.index[1]}", round(medium_top5[1],4) , round((medium_top5[1] - mid_mu_video.mean()),4))
            top2_medium.write(f"[{medium_top5.index[1]}](https://www.youtube.com/watch?v={medium_top5.index[1]})")
            top3_medium.metric(f"Top 3: {medium_top5.index[2]}", round(medium_top5[2],4) , round((medium_top5[2] - mid_mu_video.mean()),4))
            top3_medium.write(f"[{medium_top5.index[2]}](https://www.youtube.com/watch?v={medium_top5.index[2]})")
            top4_medium.metric(f"Top 4: {medium_top5.index[3]}", round(medium_top5[3],4) , round((medium_top5[3] - mid_mu_video.mean()),4))
            top4_medium.write(f"[{medium_top5.index[3]}](https://www.youtube.com/watch?v={medium_top5.index[3]})")
            top5_medium.metric(f"Top 5: {medium_top5.index[4]}", round(medium_top5[4],4) , round((medium_top5[4] - mid_mu_video.mean()),4))
            top5_medium.write(f"[{medium_top5.index[4]}](https://www.youtube.com/watch?v={medium_top5.index[4]})")
            
            
            
            
            tab4.subheader('Retention Performance by Length Category | LONG')
            long_top5 = long_mu_video.sort_values(ascending=False).head(5)
            tab4.plotly_chart(long_fig.add_traces(data=total_fig.data))
            tab4_col1, tab4_col2 = tab4.columns([1,5])
            tab4_col1.metric("Average", str(round(long_mu_video.mean(),4)), str(round((long_mu_video.mean() - overall_mu),4)), help = "Average Retention Performance by Long Video Length compared to Overall Average of the channel")
            tab4_col2.dataframe(newDF[newDF['videoIDs'].isin(long_top5.index.tolist())])
            
            tab4.subheader("Top 5 Long Videos:")
            top1_long, top2_long, top3_long, top4_long, top5_long = tab4.columns(5)
            top1_long.metric(f"Top 1: {long_top5.index[0]}", round(long_top5[0],4) , round((long_top5[0] - long_mu_video.mean()),4))
            top1_long.write(f"[{long_top5.index[0]}](https://www.youtube.com/watch?v={long_top5.index[0]})")
            top2_long.metric(f"Top 2: {long_top5.index[1]}", round(long_top5[1],4) , round((long_top5[1] - long_mu_video.mean()),4))
            top2_long.write(f"[{long_top5.index[1]}](https://www.youtube.com/watch?v={long_top5.index[1]})")
            top3_long.metric(f"Top 3: {long_top5.index[2]}", round(long_top5[2],4) , round((long_top5[2] - long_mu_video.mean()),4))
            top3_long.write(f"[{long_top5.index[2]}](https://www.youtube.com/watch?v={long_top5.index[2]})")
            top4_long.metric(f"Top 4: {long_top5.index[3]}", round(long_top5[3],4) , round((long_top5[3] - long_mu_video.mean()),4))
            top4_long.write(f"[{long_top5.index[3]}](https://www.youtube.com/watch?v={long_top5.index[3]})")
            top5_long.metric(f"Top 5: {long_top5.index[4]}", round(long_top5[4],4) , round((long_top5[4] - long_mu_video.mean()),4))
            top5_long.write(f"[{long_top5.index[4]}](https://www.youtube.com/watch?v={long_top5.index[4]})")
            
            
            
            
            
            # Top 10 Performing Videos (Relative Retention)
            top10_overall = retention_DataFrame.mean(axis=0).sort_values(ascending=False).head(10)
            top10list=top10_overall.index.tolist()
            top10df = newDF[newDF['videoIDs'].isin(top10list)][['videoIDs','videoTitle']].reset_index(drop=True)
            # st.write(top10list)
            # st.dataframe(top10df)
            
            # st.dataframe(top10_overall.reset_index(drop=True))
            tab1.subheader("Top 10 Performing Videos (Relative Retention)")
            a= pd.DataFrame(top10_overall.reset_index(drop=True)).join(top10df)
            # st.dataframe(a.iloc[:,0]*100)
            d = pd.DataFrame(top10_overall.reset_index(drop=True)).join(top10df)
            d.iloc[:,0] = round(d.iloc[:,0]*100).astype(str)+ '%'
            arr = d.columns.tolist()
            arr[0] = 'Percentile'
            arr[1] = 'Video ID'
            arr[2] = 'Video Title'
            d.columns = arr
            tab1.dataframe(d)
            st.write("Overall Retention took: ", timeit.default_timer() - overall_start)
            # top10_overall.assign(1, 'videoTitle', haha, True)
            # st.write(haha)
            # st.dataframe(top10_overall)
            # We can access the short video by doing short_mu_video['video_id']
            st.write("To download the aggregate data, click the button below:")
            st.download_button("CSV download", data=result_final.to_csv().encode('utf-8'), file_name=(f'mock_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv'))





















            st.stop()

            # # First get the overall relative retention performance
            # a = pd.pivot_table(result_final, index = 'elapsedVideoTimeRatio', values = 'relativeRetentionPerformance', aggfunc='mean')
            # total_retention_mean = a.values.mean()

            # fig = px.line(a, x=a.index, y='relativeRetentionPerformance', title=str(ANALv2.channelName))
            # st.plotly_chart(fig)

            # st.dataframe(a)
            

            # st.write("top 10")
            # b = pd.pivot_table(top10, index = 'elapsedVideoTimeRatio', values = 'relativeRetentionPerformance', aggfunc='mean')


            # fig = px.line(b, x=b.index, y='relativeRetentionPerformance', title=str(ANALv2.channelName))
            # st.plotly_chart(fig)

            # st.dataframe(b)

            # st.write("percentile of top 10 videos")
            
            
            
            
            
            
            
            
            # # relative retention performance BASED ON LENGTH
            # st.dataframe(shortDF)
            # st.header("Retention Performance: Broken Down By LENGTH")
            
            
            # short = pd.pivot_table(shortDF, index = 'elapsedVideoTimeRatio', values = 'relativeRetentionPerformance', aggfunc='mean')
            # try:
            #     medium = pd.pivot_table(mediumDF, index = 'elapsedVideoTimeRatio', values = 'relativeRetentionPerformance', aggfunc='mean')
            # except:
            #     pass
            # long = pd.pivot_table(longDF, index = 'elapsedVideoTimeRatio', values = 'relativeRetentionPerformance', aggfunc='mean')



            
            # short_fig = px.line(short, x=short.index, y='relativeRetentionPerformance', title=f'Length: Short ({int(q_array[0])} ~ {int(q_array[1])}) seconds', range_y=[0,1])
    
            # try:
            #     medium_fig = px.line(medium, x=medium.index, y='relativeRetentionPerformance', title=f'Length: Medium ({int(q_array[1])} ~ {int(q_array[2])}) seconds', range_y=[0,1])
            # except:
            #     pass
            # long_fig = px.line(long, x=long.index, y='relativeRetentionPerformance', title=f'Length: Long ({int(q_array[2])} ~ {int(q_array[3])}) seconds', range_y=[0,1])
            
            
            # # short_f = go.Figure(data=go.Scatter(x=short.index, y = short.values, name='short'))
            # # to = go.Figure(data=go.Scatter(x= a.index, y = a.values, name='total', line=dict(color='yellow')))
            # # short_f.add_trace(to)
            # # short_f.show()
            # short_fig.data[0].line.color = "#ffa600"
            # # medium_fig.data[0].line.color = '#ff6361'
            # long_fig.data[0].line.color = '#bc5090'
            # tab1, tab2, tab3 = st.tabs(["📈 Chart", "📊 Compare", "🗃 Data"])
            # tab1.subheader("Length Category: SHORT | Retention Performance")
            # tab1.plotly_chart(short_fig)
            # # tab1.subheader("Length Category: Medium | Retention Performance")
            # # tab1.plotly_chart(medium_fig)
            # tab1.subheader("Length Category: LONG | Retention Performance")
            # tab1.plotly_chart(long_fig)



            # fig.data[0].line.color = "#58508d"
            # fig.data[0].line.dash = "dash"
            # fig.data[0].name = 'Total'
            

            # total_fig = go.Figure(data = short_fig.data + long_fig.data + fig.data)
            # total_fig.update_layout(showlegend=True)
            # # f.show()
            # tab2.subheader("TOTAL DATA COMPARISON ANALYSIS")
            # tab2.plotly_chart(total_fig)

            
            
            # col1,col2 = tab3.columns(2)
            # with col1:
            #     tab3.subheader("Length Category: SHORT | DataFrame")
            #     tab3.dataframe(shortDF)
            # # tab3.subheader("Length Category: Medium | DataFrame")
            # # tab3.dataframe(mediumDF)
            # with col2:
            #     tab3.subheader("Length Category: LONG | DataFrame")
            #     tab3.dataframe(longDF)

            # # st.plotly_chart(long_fig)
            # # long_fig.data[0].line.color = '#13F6E9'
            # # long_f = go.Figure(data = long_fig.data + fig.data)
            # # long_f.update_layout(showlegend=True)
            # # st.write("Comparison to Overall")
            # # st.plotly_chart(long_f)