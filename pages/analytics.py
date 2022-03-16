import streamlit as st
import youtubeAnalytics
import youtubeData
import configparser
import oauth
import argparse
import pandas as pd
from datetime import datetime

def app():
    st.title("YouTube Analytics API")
    
    config = configparser.ConfigParser()
    config.read('conf.ini')
    SCOPE = list(config.get('SCOPE Settings', 'scopelist').split(', '))
    auth = oauth.Authorize(scope = SCOPE, token_file = 'authentications/token.yaml', secrets_file = 'authentications/secret_ama_desktop.json')
   
    auth.authorize()
    
    # auth.re_authorize()
    # auth.re_authorize()
    token = auth.load_token()
    credentials = auth.get_credentials()
    
    ANALv2 = youtubeAnalytics.YouTubeAnalytics(credentials)
    
    # Call the api_build()
    ANALv2.api_build()
    
    # if channelID is UNKNOWN
    #choose Start and End Date
    #we need videoIDList
    
    
    #inputting Date of searches
    if 'start' not in st.session_state:
        st.session_state['start'] = "2018-01-01"
        
    st.session_state['start'] = st.date_input("Start Date: ")
    ANALv2.setStartDate(str(st.session_state['start']))
    

    st.write(st.session_state['start'])
    
    
    if 'end' not in st.session_state:
        st.session_state['end'] = "2022-01-01"
    
    st.session_state['end'] = st.date_input("End Date: ")


    ANALv2.setEndDate(str(st.session_state['end']))
    st.write(st.session_state['end'])
    
    st.write(st.session_state)

    

    
    ######################
    
    
    ## CHOICE
    if 'choice' not in st.session_state:
        st.session_state['choice'] = None
        
    st.session_state['choice'] = st.radio("Choose a Dimension (default: video)", ['adType', 'ageGroup', 'asset',
                                   'audienceType', 'channel', 'claimedStatus',
                                   'contentOwner', 'country', 'day',
                                   'deviceType', 'elapsedVideoTime',
                                   'gender', 'insightPlaybackLocationDetail',
                                   'insightPlaybackLocationType',
                                   'insightTrafficSourceDetail',
                                   'insightTrafficSourceType', 'liveOrOnDemand',
                                   'operatingSystem', 'playlist',
                                   'province', 'sharingService', 'subscribedStatus',
                                   'subtitleLanguage', 'uploaderType',
                                   'video'], index=24)
    ANALv2.setDimensions(st.session_state['choice'])
    
    
    ## MEtrics
    if 'metrics' not in st.session_state:
        st.session_state['metrics']=None
        
    metrics_container = st.container()
    metrics_all = st.checkbox("Select All Metrics")
    if metrics_all:
        
        st.session_state['metrics'] = metrics_container.multiselect("Choose Metrics Options: ", ['views', 'redViews', 'comments',
                                            'likes', 'dislikes', 'videosAddedToPlaylists',
                                            'videosRemovedFromPlaylists', 'shares', 
                                            'estimatedMinutesWatched', 'estimatedRedMinutesWatched',
                                            'averageViewDuration', 'averageViewPercentage', 
                                            'annotationClickThroughRate', 'annotationCloseRate',
                                            'annotationImpressions', 'annotationClickableImpressions', 
                                            'annotationClosableImpressions', 'annotationClicks',
                                            'annotationCloses', 'cardClickRate', 'cardTeaserClickRate',
                                            'cardImpressions', 'cardTeaserImpressions', 'cardClicks', 
                                            'cardTeaserClicks', 'subscribersGained', 'subscribersLost'
                                            ],['views', 'redViews', 'comments',
                                            'likes', 'dislikes', 'videosAddedToPlaylists',
                                            'videosRemovedFromPlaylists', 'shares', 
                                            'estimatedMinutesWatched', 'estimatedRedMinutesWatched',
                                            'averageViewDuration', 'averageViewPercentage', 
                                            'annotationClickThroughRate', 'annotationCloseRate',
                                            'annotationImpressions', 'annotationClickableImpressions', 
                                            'annotationClosableImpressions', 'annotationClicks',
                                            'annotationCloses', 'cardClickRate', 'cardTeaserClickRate',
                                            'cardImpressions', 'cardTeaserImpressions', 'cardClicks', 
                                            'cardTeaserClicks', 'subscribersGained', 'subscribersLost'
                                            ])
        ANALv2.setMetrics(st.session_state['metrics'])
        
    else:
        st.session_state['metrics'] = metrics_container.multiselect("Choose Metrics Options: ",['views', 'redViews', 'comments',
                                            'likes', 'dislikes', 'videosAddedToPlaylists',
                                            'videosRemovedFromPlaylists', 'shares', 
                                            'estimatedMinutesWatched', 'estimatedRedMinutesWatched',
                                            'averageViewDuration', 'averageViewPercentage', 
                                            'annotationClickThroughRate', 'annotationCloseRate',
                                            'annotationImpressions', 'annotationClickableImpressions', 
                                            'annotationClosableImpressions', 'annotationClicks',
                                            'annotationCloses', 'cardClickRate', 'cardTeaserClickRate',
                                            'cardImpressions', 'cardTeaserImpressions', 'cardClicks', 
                                            'cardTeaserClicks', 'subscribersGained', 'subscribersLost'
                                            ], default=None)
        ANALv2.setMetrics(st.session_state['metrics'])
    if 'filter' not in st.session_state:
        st.session_state['filter'] = None
    filter_container = st.container()
    filter_all = st.checkbox("Select All")
    
    if filter_all:
        st.session_state['filter'] = filter_container.multiselect("Filters Select one or more options: ",
                                                        ['video'],['video'])
        ANALv2.setFilter(st.session_state['filter'])
    else:
        st.session_state['filter'] = filter_container.multiselect("Filters Select one or more options:",
                                                        ['video'])
        ANALv2.setFilter(st.session_state['filter'])
    st.write(st.session_state)
    if st.button('next'):
            df = pd.DataFrame()
            st.session_state
            if st.session_state['metrics'] != None and st.session_state['filter'] != None and st.session_state['choice'] != None:
                    ####### DATA v3 stuff for video id list
                if 'DATAv3' not in st.session_state:
                    st.session_state['DATAv3'] = youtubeData.YouTubeData(credentials)
                DATAv3 = st.session_state['DATAv3']
                #1) Call the api_build()
                DATAv3.api_build()
                
                if 'channelID' not in st.session_state:
                    st.session_state['channelID'] = None
                if st.session_state['channelID'] == None:
                    st.session_state['channelID'] = DATAv3.getMyChannelID()
                
                    DATAv3.setChannelID(st.session_state['channelID'])


                
                # #4) Get Channel Response on statistics
                go_next_flag = False
                if DATAv3.channelID != None:

                    DATAv3.getChannelRequest()
                    DATAv3.getStatistics()
                
                    st.write("This is Total View Count:", DATAv3.total_viewCount)
                    st.write("This is Total Suybscriber Count:", DATAv3.total_subscriberCount)
                    st.write("This is Total Video Count:", DATAv3.total_videoCount)
                    
                    DATAv3.getPlaylistID()
                    DATAv3.getChannelName()
                    
                    DATAv3.setVideoList()
                    DATAv3.setVideoIDList()
                    go_next_flag = True
                    
                    
                
                
                
                
                
                
                if go_next_flag:
                    writer = pd.ExcelWriter(f"{DATAv3.channelName}.xlsx", engine="xlsxwriter")
                    ll = []
                    ANALv2.setChannelName(DATAv3.channelName)
                    for i in DATAv3.videoIDList:
                        # st.write("end " + ANALv2.endDate)
                        # st.write("start " + ANALv2.startDate)
                        # st.write("dimension " + ANALv2.dimensions)
                        # st.write("metrics " + str(ANALv2.metrics))
                        # st.write("filters" + " video==" + str(i))
                        request = ANALv2.build.reports().query(
                            endDate = ANALv2.endDate,
                            startDate = ANALv2.startDate,
                            dimensions = ANALv2.dimensions,
                            ids = "channel==MINE",
                            metrics = ANALv2.metrics,
                            filters = "video=="+str(i)
                        )
                        response = request.execute()
                        # st.write(response)
                        # response=pd.json_normalize(response,'columnHeaders')
                       
                        columns = [i['name'] for i in response['columnHeaders']]
                        #add a videoID column in the front
                        if response['rows'] == []:
                            pass
                        else:
                            df = pd.DataFrame(response["rows"])
                            df.columns = columns
                            # df_curr = pd.DataFrame(response)
                            
                            df.insert(0,'videoID', str(i))
                            df.to_excel(writer,sheet_name=str(i)[:30])
                            ANALv2.downloadCSV(df, str(i))
                        
                        
                    
                        
                    if st.download_button():
                        writer.save()
