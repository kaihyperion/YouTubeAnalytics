import streamlit as st
from yaml import load, dump, Loader
from datetime import datetime, timedelta
import oauth
import configparser
import youtubeData

def app():
    st.title("AMA YouTube Data Extraction Tool")
    
    # Check the token expire time
    with open('authentications/token.yaml', 'r') as stream:
        token = load(stream, Loader=Loader)
        token_expiry = token['expires_at']
    
    # Now convert the token_expiry to the datetime
    token_expiry_datetime = datetime.fromtimestamp(token_expiry)
    now = datetime.now()
    config = configparser.ConfigParser()
    config.read('conf.ini')
    SCOPE = list(config.get('SCOPE Settings', 'scopelist').split(', '))

    auth = oauth.Authorize(scope = SCOPE, token_file= 'authentications/token.yaml', secrets_file = 'authentications/secret_ama2.json')
    st.write(f"Now: {now}")
    st.write(f"Token Expire: {token_expiry_datetime}")
    account_change_button = st.button('Change Account')
    # for the token to be valid, now has to be (<) token_expiry
    if now < token_expiry_datetime:
        # since it is valid, we can just authenticate
        st.header("Your Token is still Valid!")
        if account_change_button:
            st.write("Re authorize triggered")
            auth.re_authorize()
        pass
    else: # if the token is invalid, we must reauthenticate
         st.header("Your Token Expired:")
         auth.re_authorize()
    
    

        # credentials = auth.get_credentials()
        # DATAv3 = youtubeData.YouTubeData(credentials)
        # DATAv3.api_build()
        # st.session_state['channelID'] = DATAv3.getMyChannelID()
        # DATAv3.setChannelID(st.session_state['channelID'])
        # DATAv3.getChannelRequest()
        # DATAv3.getChannelName()
        # st.write(DATAv3.channelName)
        
    