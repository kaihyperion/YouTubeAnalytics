import streamlit as st
from yaml import load, dump, Loader
from datetime import datetime, timedelta
import oauth
import configparser
import youtubeData
from PIL import Image

st.set_page_config(page_title='AMA Data Extraction')
image = Image.open('images/logo.png')
st.image(image)
st.title("Jellysmack x AMA Optimization Tool")
# st.set_page_config(page_title='AMA Data Extraction')


# image = Image.open('images/logo.png')
# st.image(image)



# Check the token expire time
with open('authentications/token.yaml', 'r') as stream:
    token = load(stream, Loader=Loader)
    token_expiry = token['expires_at']

# Now convert the token_expiry to the datetime



# st.write(st.session_state)
# if st.session_state['flag']:
#     print(st.session_state['flag'])
# else:
#     print("noithing")
token_expiry_datetime = datetime.fromtimestamp(token_expiry)
if 'accountChangeFlag' not in st.session_state:
    st.session_state['accountChangeFlag'] = False
    token_expiry_datetime = datetime.fromtimestamp(token_expiry)
    
    

if st.session_state['accountChangeFlag'] == True:
    token_expiry_datetime = datetime.fromtimestamp(1218983924)

now = datetime.now()
config = configparser.ConfigParser()
config.read('conf.ini')
SCOPE = list(config.get('SCOPE Settings', 'scopelist').split(', '))

auth = oauth.Authorize(scope = SCOPE, token_file= 'authentications/token.yaml', secrets_file = 'authentications/secret_ama2.json')

token = auth.load_token()
credentials = auth.get_credentials()
DATAv3 = youtubeData.YouTubeData(credentials)
DATAv3.api_build()





col1, col2 = st.columns([4, 6])
with col1:
    st.subheader("Token expires in : \n" +str(int((token_expiry_datetime - now).seconds/60))+ " minutes")
    # st.write(f"Token Expire: {token_expiry_datetime}")
    refresh_btn = st.button("token refresh")
if refresh_btn:
    auth.token_Refresh()
    st.experimental_rerun()
# account_change_button = st.button('Change Account', on_click=auth.re_authorize())
# def new_account():
#     auth.authorize()
#     token = auth.load_token()
#     credentials = auth.get_credentials()
#     return credentials
# for the token to be valid, now has to be (<) token_expiry
with col2:
    if datetime.now() < token_expiry_datetime:
        # since it is valid, we can just authenticate
        st.subheader("Your Token is still Valid!")
        resp = DATAv3.build.channels().list(part='snippet', mine=True).execute()
        channelName = resp['items'][0]['snippet']['title']
        st.subheader("Currently signed in as: " + channelName)


    else: # if the token is invalid, we must reauthenticate
        st.subheader("Your Token Expired:")
        auth.re_authorize()


    if st.button("change account"):
        st.session_state['accountChangeFlag'] = True
        st.experimental_rerun()

# token = auth.load_token()
# credentials = auth.get_credentials()
# DATAv3 = youtubeData.YouTubeData(credentials)
# DATAv3.api_build()

# resp = DATAv3.build.channels().list(part='snippet', mine=True).execute()
# channelName = resp['items'][0]['snippet']['title']
# st.subheader("Currently signed in as: " + channelName)
# DATAv3.getChannelRequest()
# st.write(resp['items'][0]['snippet']['title'])
# DATAv3.getChannelName()
# st.write(DATAv3.channelName)


    # credentials = auth.get_credentials()
    # DATAv3 = youtubeData.YouTubeData(credentials)
    # DATAv3.api_build()
    # st.session_state['channelID'] = DATAv3.getMyChannelID()
    # DATAv3.setChannelID(st.session_state['channelID'])
    # DATAv3.getChannelRequest()
    # DATAv3.getChannelName()
    # st.write(DATAv3.channelName)
    
