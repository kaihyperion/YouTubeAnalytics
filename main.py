import os
import json
import argparse
import oauth
import requests
from googleapiclient.discovery import build
import oauth2client.client
import tabulate
import numpy as np
import pandas as pd
from io import FileIO
from googleapiclient.http import MediaIoBaseDownload
import time
import errno
def reportCreate(YT):
    print("These are the available Report Types Available to create:\n")
    reportTypeLists = YT.reportTypes().list().execute()

    df = pd.DataFrame(reportTypeLists['reportTypes'])
    print(df)
    print('\n')
    usr_input = input("Please type which specific report types (ID) you would like to create:\n(A) if you would like to Select ALL \nmake sure they are spaced: channel_annotations_a1 channel_basic_a2\nenter here: ")
    if usr_input == 'A':
        if 'reportTypes' in reportTypeLists and reportTypeLists['reportTypes']:
            reportTypes = reportTypeLists['reportTypes']
            for report in reportTypes:
                reporting_job = YT.jobs().create(body=dict(reportTypeId = report['id'], name = report['name'])).execute()
                print ('Reporting job created for reporting type "%s" at "%s"'
                       % ( reporting_job['reportTypeId'],
                          reporting_job['createTime']))

                
    print("Finished Creating jobs\n")

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
    
#kwargs is a pararmeter name and acts liek a dictioanry
# kwargs is like keyword (named) arguemnts. so key and value. must have '=' equla sign
# ** is the 'unpacking operator' it unpacks the argument passed as dictionary
# *args is positional argument



#Create a reporting job



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
    
    scope = ['https://www.googleapis.com/auth/yt-analytics.readonly', 'https://www.googleapis.com/auth/yt-analytics-monetary.readonly']
    SCOPE = ''
    for i in scope:
        SCOPE += i+' '
        
    auth = oauth.Authorize(scope = SCOPE, token_file = 'token.yaml', secrets_file = 'secret_kai.json')
    auth.authorize()
    token = auth.load_token()
    credentials = auth.get_credentials()
    
    serviceName = 'youtubereporting'
    API_VERSION = 'v1'
    youtubeReporting = build(serviceName= serviceName, version= API_VERSION,
              credentials= credentials)
    
    print("Welcome to AMA's YouTube Reporting API Data Collector! \n")
    usr_input = input("Would you like to '(C)reate' or '(R)etrieve' or (L)ist jobs?  ")
    if usr_input == 'C':
        reportCreate(youtubeReporting)
    if usr_input == 'L':
        joblist = getJobList(youtubeReporting)
        ask = input("Would you like to retrieve these jobs?: Y/N")
        if ask == 'Y':
            for i in joblist:
                reports = retrieve_reports(youtubeReporting, jobId = i[0],onBehalfOfContentOwner='')
                url_list = [i['downloadUrl'] for i in reports]
                t_list = [i['endTime'] for i in reports]
                download_report(youtubeReporting, url_list, id[1], t_list)