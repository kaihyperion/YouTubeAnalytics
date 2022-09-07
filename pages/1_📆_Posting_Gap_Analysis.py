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


# """
# THINGS TO NOTE:
# - Try to find a way to group the big dataframe all together and display it in a singular table
# - Try and except
# """ 


st.title("Posting Gap Analysis (Day of Week)")

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


date_col1, date_col2 = st.columns(2)

with date_col1:
    if 'PGAstart' not in st.session_state:
        st.session_state['PGAstart'] = '2021-06-20'
    st.session_state['PGAstart'] = st.date_input("Start Date: ", value=datetime.strptime("2020-01-01", "%Y-%m-%d"))
    ANALv2.setStartDate(st.session_state['PGAstart'])

with date_col2:
    if 'PGAend' not in st.session_state:
        st.session_state['PGAend'] = datetime.now().strftime("%Y-%m-%d")

# st.session_state['PGAend'] = st.date_input("End Date: ")
    
    ANALv2.setEndDate(st.date_input("End date: "))


if st.button('Retrieve Data'):
    with st.spinner("Loading Public Data via YouTube Data API..."):
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



        date_and_gap = DATAv3.createDF_script1()

        date_and_gap_shorts = DATAv3.createDF_script1_shorts()
    with st.spinner('Loading Private Data via YouTube Analytics API...'):
    #df holds the date and gap 
    # st.write(date_and_gap)

    # st.download_button("CSV DOWNLOAD", data=date_and_gap.to_csv().encode('utf-8'), file_name=(f'mock_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv'))

    ############################
    # """Retrieving data
    # Private pull for shorts, browse, suggested, search
    # dimension: insightTrafficSourceType,day
    # metrics: views
    # channel = MINE

    # """
        request = ANALv2.build.reports().query(
            endDate = ANALv2.endDate,
            startDate = ANALv2.startDate,
            ids = "channel==MINE",
            dimensions= 'insightTrafficSourceType,day',
            metrics = 'views'
        )
        response = request.execute()
        # st.write(response)
        columns = [i['name'] for i in response['columnHeaders']]
        if response['rows'] == []:
            # st.write("passed")
            pass
        else:
            df = pd.DataFrame(response["rows"])
            df.columns = columns
            

   

        ####
        # Creating Day name
        day = pd.to_datetime(df['day'], format='%Y-%m-%d').dt.day_name()
        df['DOW'] = day
        cats = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        df.rename(columns = {'day' : 'date'}, inplace = True)

    ### DOW AGGREAGATE
    # st.dataframe(df.groupby('DOW')['insightTrafficSourceType','day','views'].mean())
    #BROWSE category AKA('subscriber)
    # browse = df[df['insightTrafficSourceType'] == "SUBSCRIBER"]
    # browse['DOW'] = pd.Categorical(browse['DOW'], categories=cats, ordered=True)
    # suggested = df[df['insightTrafficSourceType'] == "RELATED_VIDEO"]
    # suggested['DOW'] = pd.Categorical(suggested['DOW'], categories=cats, ordered=True)
    # shorts = df[df['insightTrafficSourceType'] == "SHORTS"]
    # shorts['DOW'] = pd.Categorical(shorts['DOW'], categories=cats, ordered=True)
    # search = df[df['insightTrafficSourceType'] == "YT_SEARCH"]
    # search['DOW'] = pd.Categorical(search['DOW'], categories=cats, ordered=True)

    tab1, tab2, tab3 = st.tabs(["📅DOW", " 📈Posting Gap Analysis", "📊Posting Gap Analysis (Shorts)"])
    # st.dataframe(df.groupby('DOW')['insightTrafficSourceType','views'].mean())
    # st.dataframe(df.groupby('insightTrafficSourceType')['views'].mean())
    grouped=df.loc[df.insightTrafficSourceType.isin(['SUBSCRIBER','RELATED_VIDEO','SHORTS','YT_SEARCH'])]\
        .pivot_table(index='DOW', 
                     columns='insightTrafficSourceType', 
                     values='views', 
                     aggfunc='mean')\
        .rename(columns = {'RELATED_VIDEO':'Suggested',
                            'SHORTS':'Shorts',
                            'SUBSCRIBER':'Browse',
                            'YT_SEARCH':'Search'})\
        .reindex(cats).style\
            .format("{:,.0f}")\
                .highlight_max(axis=0, color='#00DF4F')\
                    .highlight_min(axis=0, color='#DE1D16')
 
    
    with tab1:
        tab1.subheader("Days of Week Analysis on Content Types")
        
        col1, col2 = st.columns([6,4])
        with col1:
            st.table(grouped)
        
        with col2:
            st.table(df.loc[df.insightTrafficSourceType.isin(['SUBSCRIBER','RELATED_VIDEO','SHORTS','YT_SEARCH'])]\
            .pivot_table(index='DOW',
                        columns='insightTrafficSourceType', 
                        values='views', 
                        aggfunc='mean')\
            .reindex(cats).mean(axis=1).to_frame(name='Overall Average').style.format("{:,.0f}").background_gradient(cmap='Oranges'))



    #####
    # Posting GAPS

    df.rename(columns = {'day' : 'date'}, inplace = True)
    df_copy = df
    df = date_and_gap.merge(df[['date', 'views', 'insightTrafficSourceType']], how='left', on='date').fillna(0)
    # postingGap_browse = df[df['insightTrafficSourceType'] == 'SUBSCRIBER']
    # postingGap_suggested = df[df['insightTrafficSourceType'] == 'RELATED_VIDEO']
    # postingGap_shorts = df[df['insightTrafficSourceType'] == 'SHORTS']
    # postingGap_search = df[df['insightTrafficSourceType'] == 'YT_SEARCH']
    # print(df)
    with tab2:
        tab2.subheader("Posting Gap Average analysis")
        
        col1, col2 = st.columns([3,1])
        
        postingGap_df = df.loc[df.insightTrafficSourceType.isin(['SUBSCRIBER','RELATED_VIDEO','SHORTS','YT_SEARCH'])]\
            .pivot_table(index='gap_days',
                         columns='insightTrafficSourceType',
                         values = 'views',
                         aggfunc='mean')\
            .rename(columns = {'RELATED_VIDEO':'Suggested',
                            'SHORTS':'Shorts',
                            'SUBSCRIBER':'Browse',
                            'YT_SEARCH':'Search'})
            
        postingGap_df.index = postingGap_df.index.astype(int)
        postingGap_df.index.name = 'gap_Days'
        
        with col1:
            st.table(postingGap_df.fillna(0).sort_index().style.format("{:,.0f}")\
                                        .highlight_max(axis=0, color='#00DF4F')\
                                            .highlight_min(axis=0, color='#DE1D16'))
        
        with col2:
            st.table(postingGap_df.sort_index().mean(axis=1).to_frame(name='Overall Average').style.format("{:,.0f}").background_gradient(cmap='BuGn'))

        


    #######
    # SHORTS analysis
    if date_and_gap_shorts:
        df = date_and_gap_shorts.merge(df_copy[['date', 'views', 'insightTrafficSourceType']], how='left', on='date').fillna(0)
    # postingGap_browse = df[df['insightTrafficSourceType'] == 'SUBSCRIBER']
    # postingGap_suggested = df[df['insightTrafficSourceType'] == 'RELATED_VIDEO']
    # postingGap_shorts = df[df['insightTrafficSourceType'] == 'SHORTS']
    # postingGap_search = df[df['insightTrafficSourceType'] == 'YT_SEARCH']

    with tab3:
        col1, col2 = st.columns([3,1])
        tab3.subheader("SHORTS Posting Gap Average analysis")
        postingGapShorts_df = df.loc[df.insightTrafficSourceType.isin(['SUBSCRIBER','RELATED_VIDEO','SHORTS','YT_SEARCH'])]\
            .pivot_table(index='gap_days',
                         columns='insightTrafficSourceType',
                         values = 'views',
                         aggfunc='mean')\
            .rename(columns = {'RELATED_VIDEO':'Suggested',
                            'SHORTS':'Shorts',
                            'SUBSCRIBER':'Browse',
                            'YT_SEARCH':'Search'})
        postingGapShorts_df.index = postingGapShorts_df.index.astype(int)
        postingGapShorts_df.index.name = 'gap_Days'
        with col1:
            st.table(postingGapShorts_df.fillna(0).sort_index().head(10).style.format("{:,.0f}")\
                                        .highlight_max(axis=0, color='#00DF4F')\
                                            .highlight_min(axis=0, color='#DE1D16'))
        
        with col2:
            st.table(postingGapShorts_df.sort_index().head(10).mean(axis=1).to_frame(name='Overall Average').style.format("{:,.0f}").background_gradient(cmap='Reds'))
            
        # col0, col1, col2, col3, col4 = tab3.columns(5)

        # col0.subheader("OVERALL")
        # col1.subheader('Browse')
        # col2.subheader('Suggested')
        # col3.subheader('Shorts')
        # col4.subheader('Search')
        # col0.dataframe(df.groupby('gap_days')['views'].mean())
        # col1.dataframe(postingGap_browse.groupby('gap_days')['views'].mean())
        # col2.dataframe(postingGap_suggested.groupby('gap_days')['views'].mean())
        # col3.dataframe(postingGap_shorts.groupby('gap_days')['views'].mean())
        # col4.dataframe(postingGap_search.groupby('gap_days')['views'].mean())
        
with st.expander("ℹ️"):
    st.write("Details regarding Posting Gap Analysis (PGA for short).\ This allows (private) users to view Posting Gap Analysis of their channel. There are Days of Week Analysis as well.")
