import configparser
from googleapiclient.discovery import build
import pandas as pd
import argparse
from googleapiclient.http import MediaIoBaseDownload
import os
import time
from io import FileIO
import errno


config = configparser.ConfigParser()
config.read('conf.ini')

class YouTubeReporting():
    def __init__(self, credentials):
        self.api_name = config.get('YouTube Analytics', 'api_service_name')
        self.api_version = config.get('YouTube Analytics', 'api_version')
        self.credentials = credentials
        self.build = None
        
        
        
        
        
    def api_build(self):
        """Using Google API Client, it returns a build obj 
        sets the self.build with this 
        
        Call this function to set the build connection

        Returns:
            object: use this to do farther implementation
        """
        self.build = build(serviceName = self.api_name, version = self.api_version, credentials = self.credentials)
    
    
    
    
    
    
    def getJobList(self):
        """Currently Created Reporting jobs that is available after previous create

        Returns:
            List: List of ID of reporting jobs available
        """
        
        print("These are the currently CREATED Reporting jobs available:\n")
        results = self.build.jobs().list().execute()
        if 'jobs' in results and results['jobs']:
            
            jobs = results['jobs']
            idList = []
            
            for job in jobs:
                
                print('Reporting job id: %s\n name: %s\n for reporting type: %s\n'
                    % (job['id'], job['name'], job['reportTypeId']))
                
                idList.append([job['id'],job['reportTypeId']])
            
        return idList
    
    
    
    
    
    def retrieveReport(self, **kwargs):
        
        results = self.build.jobs().reports().list(**kwargs).execute()
        
        if 'reports' in results and results['reports']:
            
            reports = results['reports']
            
            for report in reports:
                
                print ('Report dates: %s to %s\n       download URL: %s\n'
                    % (report['startTime'], report['endTime'], report['downloadUrl']))
                
                
            url_list = [i['downloadUrl'] for i in reports]
            time_list = [i['endTime'] for i in reports]
            
            return url_list, time_list, reports
        
        else:
            print("no reports found")
    
    
    def download_report(self, report_url, reportTypeName, timeList):
        request = self.build.media().download(
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
    
    
    def reportCreate(self):
        """Prints out the available Report TYPES that are available to create
        
        """
        response_reportTypeLists = self.build.reportTypes().list().execute()
        
        df = pd.DataFrame(response_reportTypeLists['reportTypes'])
        
        print(df)
        print('\n')
        
        usr_input = input("Please type which specific report types (ID) you would like to create:\n(A) if you would like to Select ALL \nmake sure they are spaced: channel_annotations_a1 channel_basic_a2\nenter here: ")
        if usr_input == 'A':
            
            if 'reportTypes' in response_reportTypeLists and response_reportTypeLists['reportTypes']:
                
                reportTypes = response_reportTypeLists['reportTypes']
                
                for report in reportTypes:
                    
                    reporting_job = self.build.jobs().create(body=dict(reportTypeId = report['id'], name = report['name'])).execute()
                    
                    print ('Reporting job created for reporting type "%s" at "%s"'
                        % ( reporting_job['reportTypeId'],
                            reporting_job['createTime']))
                    
            print("Finished Creating jobs\n")
            
            
        else:
            # parse the list of specific report types
            selected_reportTypes = list(usr_input.split(" "))
            
            for i in response_reportTypeLists['reportTypes']:
                
                if i in selected_reportTypes:
                    
                    reporting_job = self.build.jobs().create(body=dict(reportTypeId = report['id'], name = report['name'])).execute()
                    
                    print ('Reporting job created for reporting type "%s" at "%s"'
                        % ( reporting_job['reportTypeId'],
                            reporting_job['createTime']))
                    
            print("Finished Creating jobs\n")
        
        
