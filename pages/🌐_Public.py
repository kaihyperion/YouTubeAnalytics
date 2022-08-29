import streamlit as st
import youtubeData
import configparser
import oauth
import argparse
import pandas as pd
from datetime import datetime

from PIL import Image
from io import BytesIO
import base64

def show_image_from_url(image_url):
    return (f'')

def path_to_image_html(path):
    return ('<img src="'+ path + '" width="120" >')

def convert_df(input_df):
    return input_df.to_html(escape=False, formatters=dict(img=path_to_image_html))


def get_thumbnail(path: str) -> Image:
    img = Image.open(path)
    img.thumbnail((200, 200))
    return img

def image_to_base64(img_path: str) -> str:
    img = get_thumbnail(img_path)
    with BytesIO() as buffer:
        img.save(buffer, "PNG")
        return base64.b64encode(buffer.getvalue()).decode()
    
def image_formatter(img_path: str) -> str:
    return f'<img src="data:image/png;base64,{image_to_base64(img_path)}">'

@st.cache
def convert_df(input_df):
    return input_df.to_html(escape=False, formatters=dict(thumbnail=image_formatter))

    
st.title("YouTube Data V3 API")

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

### Session state
if "ChannelName" not in st.session_state and 'ChannelID' not in st.session_state:
    st.session_state['ChannelName'] = None
    st.session_state['ChannelID'] = None

#### ALL streamlit inputs here
col1, col2 = st.columns(2)
with col1:
    inputChannelName = st.text_input("If Channel ID is unknown, ENTER Channel Name: ")
with col2:
    inputChannelID = st.text_input("If Channel ID is known: ENTER CHANNEL ID")
#2) if channelID is UNKNOWN
if inputChannelName:
    with st.spinner('Please wait...'):
        st.write("Here are relevant Channel ID with corresponding Channel Name")
        relevant_ch_IDs = DATAv3.getChannelIDs(inputChannelName)
        ids = relevant_ch_IDs[0]
        desc = relevant_ch_IDs[1]
        urls = relevant_ch_IDs[2]
        idlist = []
        description = []
        u = []
        for i in range(len(ids)):
            idlist.append(ids[i])
            description.append(desc[i])
            u.append(urls[i]["url"])
        data = {'channel ID':idlist, 'description':description,'thumbnail':u}
    df = pd.DataFrame(data)
    # st.dataframe(df)
    df_2 = df[['thumbnail','channel ID','description']]
    st.markdown(
        df_2.to_html(escape=False, formatters=dict(thumbnail=path_to_image_html)),
        unsafe_allow_html=True,
    )
    channelID = st.selectbox("Select from Following Channel ID", df)
    # st.write(channelID)
    DATAv3.setChannelID(channelID)
    st.session_state['ChannelID'] = channelID
    
elif inputChannelID:
    DATAv3.setChannelID(inputChannelID)
    st.session_state['ChannelID'] = inputChannelID
# st.write(st.session_state)

#4) Get Channel Response on statistics
if st.session_state['ChannelID']:
    with st.spinner('Please wait...'):
        DATAv3.getChannelRequest()
        DATAv3.getStatistics()
        
        st.write("This is Total View Count:", DATAv3.total_viewCount)
        st.write("This is Total Subscriber Count:", DATAv3.total_subscriberCount)
        st.write("This is Total Video Count:", DATAv3.total_videoCount)
        
        DATAv3.getPlaylistID()
        DATAv3.getChannelName()
        
        DATAv3.setVideoList()
        DATAv3.setVideoIDList()
        
        DATAv3.setVideoDataList()
        DATAv3.videoDataParser()
        DATAv3.parseVideoLength()
        df = DATAv3.createDF_script2()
        # st.dataframe(df)
    # df = df[df['length_in_seconds'] > 90]
    st.dataframe(df)
    with st.expander("See Thumbnails"):
        st.markdown(
            df.to_html(escape=False, formatters=dict(thumbnail=path_to_image_html)),
            unsafe_allow_html=True,
        )
    st.download_button("CSV DOWNLOAD", data=df.to_csv().encode('utf-8'), file_name=(f'{DATAv3.channelName}_{datetime.now().strftime("%m.%d.%Y_%H:%M")}.csv'))

    
    
    # a = df['thumbnail']
    # a.to_html()
    # st.dataframe(a)
    # st.dataframe(df)
    # st.table(df)
    # image_df = pd.DataFrame({'url': df['thumbnail'], 'thumbnail': df['thumbnail']})
    # html = convert_df(image_df)

    