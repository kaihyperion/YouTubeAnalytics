import streamlit as st
import youtubeAnalytics
import youtubeData
import configparser
import oauth
import argparse
import pandas as pd
from datetime import datetime


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
    st.session_state['start'] = "2019-12-01"
    
st.session_state['start'] = st.date_input("Start Date: ")
ANALv2.setStartDate(str(st.session_state['start']))


st.write(st.session_state['start'])


if 'end' not in st.session_state:
    st.session_state['end'] = "2022-03-06"

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
                                'deviceType', 'elapsedVideoTimeRatio',
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
                                        'cardTeaserClicks', 'subscribersGained', 'subscribersLost', 'relativeRetentionPerformance'
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
                                        'cardTeaserClicks', 'subscribersGained', 'subscribersLost', 'relativeRetentionPerformance'
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
                                        'cardTeaserClicks', 'subscribersGained', 'subscribersLost', 'relativeRetentionPerformance'
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
                st.write("This is Total Subscriber Count:", DATAv3.total_subscriberCount)
                st.write("This is Total Video Count:", DATAv3.total_videoCount)
                
                DATAv3.getPlaylistID()
                DATAv3.getChannelName()
                
                DATAv3.setVideoList()
                DATAv3.setVideoIDList()
                go_next_flag = True
                
                
            
            
            
            
            
            
            if go_next_flag:
                writer = pd.ExcelWriter(f"{DATAv3.channelName}.xlsx", engine="xlsxwriter")
                result = pd.DataFrame()
                ANALv2.setChannelName(DATAv3.channelName)
                data = pd.read_excel('retention drew binsky.xlsx', skiprows=2)
                dd = pd.DataFrame(data)
                A = dd['Group A'].dropna().values.tolist()
                B = dd['Group B'].dropna().values.tolist()
                C = dd['Group C'].dropna().values.tolist()
                D = dd['Group D'].dropna().values.tolist()
                E = dd['Group E'].dropna().values.tolist()
                F = dd['Group F'].dropna().values.tolist()




                for i in F:

                    request = ANALv2.build.reports().query(
                        endDate = ANALv2.endDate,
                        startDate = ANALv2.startDate,
                        dimensions = ANALv2.dimensions,
                        ids = "channel==MINE",
                        metrics = ANALv2.metrics,
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
                        
                        if result.empty:
                            result = df
                        else:
                            
                            result = pd.concat([result, df])
                # result.to_excel(writer,sheet_name=str(i)[:30])
                st.dataframe(result)
                # ANALv2.downloadCSV(result, str(DATAv3.channelName))
                st.download_button("CSV DOWNLOAD", data=result.to_csv().encode('utf-8'), file_name=(f'{DATAv3.channelName}_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv'))

                    
                
                    
                # if st.download_button():
                #     writer.save()
