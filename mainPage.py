import streamlit as st
from yaml import load, dump, Loader
from datetime import datetime, timedelta
import oauth
import configparser
import youtubeData
from PIL import Image

st.set_page_config(page_title='AMA Data Extraction')
st.title("JELLYSMACK X AMA DATA ACQUISITION TOOL")
# st.set_page_config(page_title='AMA Data Extraction')


image = Image.open('images/logo.png')
st.image(image)
st.title("YouTube Data Extraction Tool")


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
# st.session_state['flag'] = "Hi"
# st.write(f"Now: {now}")
st.write(f"Token Expire: {token_expiry_datetime}")
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

if datetime.now() < token_expiry_datetime:
    # since it is valid, we can just authenticate
    st.header("Your Token is still Valid!")
    

else: # if the token is invalid, we must reauthenticate
    st.header("Your Token Expired:")
    auth.re_authorize()


if st.button("change account"):
    st.session_state['accountChangeFlag'] = True
    st.experimental_rerun()

    # credentials = auth.get_credentials()
    # DATAv3 = youtubeData.YouTubeData(credentials)
    # DATAv3.api_build()
    # st.session_state['channelID'] = DATAv3.getMyChannelID()
    # DATAv3.setChannelID(st.session_state['channelID'])
    # DATAv3.getChannelRequest()
    # DATAv3.getChannelName()
    # st.write(DATAv3.channelName)
    
