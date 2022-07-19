import numpy as np
import pandas as pd
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

# using YouTube v2 API
# retreive basic video stats
# api_service_name = 'youtubeAnalytics'
# api_version = 'v2'

def process():
    # youtube_analytics = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
    # request = youtube_analytics.reports().query(
    #     ids='channel==MINE',
    #     startDate='2015-06-01',
    #     endDate='2015-06-30',
    #     metrics='views,estimatedMinutesWatched,averageViewDuration,annotationClickThroughRate,annotationCloseRate,comments,dislikes,likes,shares,subscribersGained,subscribersLost,viewerPercentage,views',
    #     dimensions='day',
    #     sort='day'
    # )
    # response = request.execute()
    # print(response)
    # df = pd.DataFrame(response['rows'])
    # df.columns = response['columnHeaders']
    # print(df)
    # df.to_csv('test.csv')
    # df = pd.read_csv('test.csv')
    # print(df)
    # df.plot(x='day', y='views')
    # plt.show()
    # df.plot(x='day', y='estimatedMinutesWatched')
    # plt.show()
    # df.plot(x='day', y='averageViewDuration')
    # plt.show()
    # df.plot(x='day', y='annotationClickThroughRate')
    # plt.show()
    # df.plot(x='day', y='annotationCloseRate')
    # plt.show()
    # df.plot(x='day', y='comments')
    # plt.show()
    # df.plot(x='day', y='dislikes')
    # plt.show()
    # df.plot(x='day', y='likes')
    # plt.show()
    # df.plot(x='day', y='shares')
    # plt.show()
    # df.plot(x='day', y='subscribersGained')