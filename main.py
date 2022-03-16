import os
import json
import argparse
import oauth
import requests
from googleapiclient.discovery import build
import tabulate
import numpy as np
import pandas as pd
from io import FileIO
from googleapiclient.http import MediaIoBaseDownload
import time
import errno




import configparser
import youtubeReporting as YTReporting
##analytics libraries
import google_auth_oauthlib.flow
import googleapiclient.errors

# def reportCreate(YT):
#     print("These are the available Report Types Available to create:\n")
#     reportTypeLists = YT.reportTypes().list().execute()

#     df = pd.DataFrame(reportTypeLists['reportTypes'])
#     print(df)
#     print('\n')
#     usr_input = input("Please type which specific report types (ID) you would like to create:\n(A) if you would like to Select ALL \nmake sure they are spaced: channel_annotations_a1 channel_basic_a2\nenter here: ")
#     if usr_input == 'A':
#         if 'reportTypes' in reportTypeLists and reportTypeLists['reportTypes']:
#             reportTypes = reportTypeLists['reportTypes']
#             for report in reportTypes:
#                 reporting_job = YT.jobs().create(body=dict(reportTypeId = report['id'], name = report['name'])).execute()
#                 print ('Reporting job created for reporting type "%s" at "%s"'
#                        % ( reporting_job['reportTypeId'],
#                           reporting_job['createTime']))

                
#     print("Finished Creating jobs\n")

def getJobList(YT):
    print("These are the currently created Reporting jobs available:\n")
    results = YT.jobs().list().execute()
    if 'jobs' in results and results['jobs']:
        jobs = results['jobs']
        idList = []
        for job in jobs:
            print('Reporting job id: %s\n name: %s\n for reporting type: %s\n'
                % (job['id'], job['name'], job['reportTypeId']))
        idList.append([job['id'],job['reportTypeId']])
    return idList

def retrieve_reports(YT, **kwargs):
    results = YT.jobs().reports().list(**kwargs).execute()
    if 'reports' in results and results['reports']:
        reports = results['reports']
        for report in reports:
            print ('Report dates: %s to %s\n       download URL: %s\n'
                % (report['startTime'], report['endTime'], report['downloadUrl']))
        return reports
    else:
      print("no reports found")

def download_report(YT, report_url, reportTypeName, timeList):
    request = YT.media().download(
    resourceName=' '
    )
    for i in range(len(report_url)):
        request.uri = report_url[i]
        fileName = 'data/'+reportTypeName+'/'+timeList[i]+'.csv'
        if not os.path.exists(os.path.dirname(fileName)):
            try:
                os.makedirs(os.path.dirname(fileName))
            except OSError as exc:
                if exc.errno != errno.EEXist:
                    raise
            
        fh = FileIO(fileName, mode= 'wb')
        downloader = MediaIoBaseDownload(fh, request, chunksize=-1)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if status:
                print ('Download %d%%.' % int(status.progress() * 100))
        print ('Download Complete!')

    time.sleep(20)
    
import streamlit as st

if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    
    # parser.add_argument('--content-owner', default= '',
    #                     help = 'ID of content owner for which you are retrieving jobs and reports.')
    # parser.add_argument('--include-system-managed', default = False,
    #                     help = 'Whether the API response should include system-managed reports')
    # parser.add_argument('--name', default = '',
    #                     help= 'Name for the reporting job. The script prompts you to set a name ' +
    #                     'for the job if you do not provide one using this argument')
    # parser.add_argument('--report-type', default=None,
    #                     help = 'The type of report for which you are creating a job')
    # args = parser.parse_args()
    # parser = argparse.ArgumentParser(description = 'AMA Data collecting program Description')
    # parser.add_argument('--service' , choices = ('analytics', 'reporting', 'data'),
    #                     metavar = 'API_NAME', type=str, required=True,
    #                     help = 'API Service name CHOOSE ONE: (i.e. analytics, reporting, data)')
    # parser.add_argument('--channelName', metavar = 'Channel Name',type=str,
    #                     help = "YouTuber Channel Name")
    # parser.add_argument('--channelID', metavar = 'Channel ID', type = str,
    #                     help = "YouTuber Channel ID (i.e. UCxxxxxxxxx)")
    # parser.add_argument('--tokenFile', metavar = 'Token File',type=argparse.FileType('r'),
    #                     default='/authentications/token.yaml',
    #                     help = 'YAML Token file location (default: /authentications/token.yaml')
    # parser.add_argument('--secretFile', metavar = 'Secret File', type = argparse.FileType('r'),
    #                     default = '/authentications/secret_kai.json',
    #                     help = 'JSON Secret File location (default: /authentications/secret_kai.json)')
    # args = parser.parse_args()


    #configuration
    config = configparser.ConfigParser()
    config.read('conf.ini')

    SCOPE = list(config.get('SCOPE Settings', 'scopelist').split(', '))
    

    auth = oauth.Authorize(scope = SCOPE, token_file = 'authentications/token.yaml', secrets_file = 'authentications/secret_kai.json')
    auth.authorize()
    token = auth.load_token()
    credentials = auth.get_credentials()

    st.title('AMA YouTube Data Extraction Tool')
    page = st.selectbox("Choose your page", ["Page 1", "Page 2", "Page 3"]) 
    if page == "Page 1":
    # Display details of page 1
    elif page == "Page 2":
        # Display details of page 2
    elif page == "Page 3":
    # Display details of page 3
#     api_selection = st.sidebar.selectbox(
#     'What API would you like to use?',
#     ('Data V3', 'Analytics V2', 'Reporting V1')
# )
#     st.subheader(api_selection)
# left_column, right_column = st.columns(2)
# # You can use a column just like st.sidebar:
# data_api = left_column.button('Data V3 API')
# analytic_api = left_column.button('Analytics V2 API')
# reporting_api = left_column.button('Reporting V1 API')
# if data_api:
#     st.subheader("pressed")
    
    
# # Or even better, call Streamlit functions inside a "with" block:
# with right_column:
#     chosen = st.radio(
#         'Sorting hat',
#         ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin"))
#     st.write(f"You are in {chosen} house!")
    
    # print("Welcome to AMA's YouTube Reporting API Data Collector! \n")
    # usr_input = input("Would you like to '(P)rototype' or (C)reate' or '(R)etrieve' or (L)ist jobs?  ")
    # if args.service == 'reporting':
        

    #     api = YTReporting.YouTubeReporting(credentials = credentials)
    #     api.api_build()
    #     api.reportCreate()
        
    #     usr_input = input("Would you like to download?: Y or N")
        
    #     if usr_input == 'Y':
            
    #         joblist = api.getJobList()
            
    #         for i in joblist:
    #             url_list, time_list, reports = api.retrieveReport(jobId = i[0], onBehalfOfContentOwner='')
    #             api.download_report(url_list, id[1], time_list)
        
        
                
    # if usr_input == 'P':
    #     print("Dimension of this proto pull is by Day")
    #     channel_unique_id = str(input("Channel Unique ID: "))
    #     startDate = str(input("Starting Date (format: 2019-01-01): "))
    #     endDate = str(input("End Date (format: 2022-01-01): "))
        
    #     # use the DATA V3 API to pull out the list of videoID
    #     api_key = 'AIzaSyBJixTpGuWue17mPX1Ia_O7vUcrcvcOdMs'
    #     datav3 = build('youtube', 'v3', developerKey= api_key)
    #     videoList = []
    #     nextToken = None
    #     channel_request = datav3.channels().list(part='statistics, contentDetails, snippet', id = channel_unique_id).execute()
    #     playlistID = channel_request['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
    #     while True:
    #         result = datav3.playlistItems().list(playlistId= playlistID, maxResults= 50, part= 'snippet', pageToken= nextToken).execute()
    #         videoList += result['items']
    #         nextToken = result.get('nextPageToken')
    #         if nextToken is None:
    #             break
            
    #     videoIdList = list(map(lambda k:k['snippet']['resourceId']['videoId'], videoList))
            
    #     try:
    #         serviceName = 'youtubeAnalytics'
    #         API_VERSION = 'v2'
    #         youtubeAnalytics= build(serviceName= serviceName, version= API_VERSION,
    #                 credentials= credentials)
            
    #         for i in videoIdList:
    #             request = youtubeAnalytics.reports().query(
    #                 endDate = "2022-01-01",
    #                 startDate = "2019-01-01",
    #                 dimensions='day',
    #                 ids="channel==MINE",
    #                 metrics="views,redViews,comments,likes,dislikes,videosAddedToPlaylists,videosRemovedFromPlaylists,shares,estimatedMinutesWatched,estimatedRedMinutesWatched,averageViewDuration,averageViewPercentage,annotationClickThroughRate,annotationCloseRate,annotationImpressions,annotationClickableImpressions,annotationClosableImpressions,annotationClicks,annotationCloses,cardClickRate,cardTeaserClickRate,cardImpressions,cardTeaserImpressions,cardClicks,cardTeaserClicks,subscribersGained,subscribersLost"
    #                 , filters="video=="+str(i)
    #             )
    #             response = request.execute()
    #             df = pd.DataFrame(response)
    #             df.to_csv()
    #             print(response)
    #     except errno:
    #         print("re authorizing")
    #         auth.re_authorize()
            
    
    