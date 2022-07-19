import youtubeData
import configparser
import oauth
import argparse
import pandas as pd 
import datetime
from urllib.parse import urlsplit, urlparse
import time
from alive_progress import alive_bar

config = configparser.ConfigParser()
config.read('conf.ini')
SCOPE = list(config.get('SCOPE Settings', 'scopelist').split(', '))
auth = oauth.Authorize(scope = SCOPE, token_file = 'authentications/token.yaml', secrets_file = 'authentications/secret_ama2.json')
auth.authorize()
# auth.re_authorize()
token = auth.load_token()
credentials = auth.get_credentials()
DATAv3 = youtubeData.YouTubeData(credentials)
#1) Call the api_build()
DATAv3.api_build()

df = pd.read_excel('datapull.xlsx')
df = df.dropna()

tiktoker_list = []
channel_list = []
total_video_list= []

first_video_list = []

total_view_list = []
total_subscriber_list = []

with alive_bar(df.shape[0], bar = 'filling', spinner = 'pulse') as bar:
    for index, row in df.iterrows():
        # check if there is a youtube Channel
        tiktoker_list.append(row['TikToker Name'])
        print(row['TikToker Name'])
        channel_list.append(row['YouTube Channel'])
        print(row['YouTube Channel'])
        channelID = urlparse(row['YouTube Channel']).path.split('/')[2]
        print('Channel ID list is :'+ urlparse(row['YouTube Channel']).path.split('/')[2])
        DATAv3.setChannelID(channelID)
        
        DATAv3.getChannelRequest()
        DATAv3.getStatistics()
        total_video_list.append(DATAv3.total_videoCount)
            
        total_view_list.append(DATAv3.total_viewCount)
        total_subscriber_list.append(DATAv3.total_subscriberCount)
        try:
            DATAv3.getPlaylistID()

            DATAv3.setVideoList()
            DATAv3.setVideoIDList()
            DATAv3.setVideoDataList()
            DATAv3.videoDataParser()
            
            first_video_list.append(DATAv3.publishedDate[-1])
            
        except:
            print("Playlist is not found so no video")
            first_video_list.append(0)
        
        
        bar()
    

    
    

data = {'TikToker Name': tiktoker_list,
        'YouTube Channel': channel_list,
        'Videos Published': total_video_list,
        'First Video Publish Date': first_video_list,
        'Total Views': total_view_list,
        'Total Subscribers': total_subscriber_list}
csv = pd.DataFrame(data)
csv.to_csv('Mateo Dat aPull')
