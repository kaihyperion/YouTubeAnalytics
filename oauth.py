import os
import secrets
import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from requests_oauthlib import OAuth2Session #https://docs.authlib.org/en/latest/client/oauth2.html
from urllib3.util.retry import Retry
from yaml import load, dump, YAMLError
from oauth2client.client import OAuth2Credentials
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
    

'''
https://developers.google.com/identity/protocols/oauth2/web-server#httprest_3

'''
# Google's OAUTH 2.0 endpoint url
authorization_base_url = 'https://accounts.google.com/o/oauth2/v2/auth'
token_uri = 'https://www.googleapis.com/oauth2/v4/token'

class Authorize:
    def __init__(self, scope, token_file, secrets_file):
        self.scope = scope
        self.token_file = token_file
        self.session = None
        self.token = None
        
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        
        try:
            with open(secrets_file, 'r') as stream:
                all_yaml = load(stream, Loader= Loader)
            secrets = all_yaml['installed']
            self.client_id = secrets['client_id']
            self.client_secret = secrets['client_secret']
            self.redirect_uri = secrets['redirect_uris'][0]
            self.token_uri = secrets['token_uri']
            self.extra = {
                'client_id': self.client_id,
                'client_secret': self.client_secret}
            
        except (YAMLError, IOError):
            print('Missing or Bad Secrets File: {}.\n Please double check'.format(secrets_file))
            exit(1)
            
    def load_token(self):
        try:
            with open(self.token_file, 'r') as stream:
                token = load(stream, Loader=Loader)
                self.access_token = token['access_token']
                self.redirect_token = token['refresh_token']
                self.token_expiry = token['expires_at']
                
        except (YAMLError, IOError):
            return None
        return token
    
    def save_token(self, token):
        
        with open(self.token_file, 'w') as stream:
            dump(token, stream, Dumper = Dumper)
        os.chmod(self.token_file, 0o600)
    def re_authorize(self):
        self.session = OAuth2Session(self.client_id, scope=self.scope,
                                        redirect_uri = self.redirect_uri,
                                        auto_refresh_url = self.token_uri,
                                        auto_refresh_kwargs = self.extra,
                                        token_updater=self.save_token)
        
        authorization_url, _ = self.session.authorization_url(
            authorization_base_url,
            access_type="offline",
            prompt="select_account")
        
        with st.expander("Please Click the Link and Authorize"):
            st.write("Please click the link: ", authorization_url)
        with st.form("token_form"):
            
            response_code = st.text_input("Paste the response token: ")
            token_submit = st.form_submit_button('Submit Token')
        # response_code = input('Paste the response token: ')
            if token_submit:
                st.write("Token Submitted!")
                self.token = self.session.fetch_token(
                    self.token_uri, client_secret = self.client_secret,
                    code = response_code)
                
                # st.write(self.token)
                self.save_token(self.token)
                
                #Save it into Streamlit session rather than file
                st.session_state['user_token'] = self.token
                
        
    def token_Refresh(self):
        tok=self.load_token()
        st.write(self.token_uri)
        self.session = OAuth2Session(self.client_id, token= tok,
                                     auto_refresh_url=self.token_uri,
                                     auto_refresh_kwargs=self.extra,
                                     token_updater = self.save_token)
        
        new_token = self.session.refresh_token(self.token_uri, refresh_token=tok['refresh_token'])
        self.save_token(new_token)
        
        
            
        
    def authorize(self):
        token = self.load_token()
        
     
        if token:
            self.session = OAuth2Session(self.client_id, token= token,
                                         auto_refresh_url = self.token_uri,
                                         auto_refresh_kwargs = self.extra,
                                         token_updater = self.save_token)
            
        else:
            print(self.scope)
            self.session = OAuth2Session(self.client_id, scope=self.scope,
                                         redirect_uri = self.redirect_uri,
                                         auto_refresh_url = self.token_uri,
                                         auto_refresh_kwargs = self.extra,
                                         token_updater=self.save_token)
            
            authorization_url, _ = self.session.authorization_url(
                authorization_base_url,
                access_type="offline",
                prompt="select_account")
            with st.expander("Please Click the Link and Authorize:"):
                print("Please click the link and authorize: ", authorization_url)
            
                response_code = input('Paste the response token: ')
            
                self.token = self.session.fetch_token(
                    self.token_uri, client_secret = self.client_secret,
                    code = response_code)
                self.save_token(self.token)
            
        
        retries = Retry(total = 3,
                        backoff_factor = 0.1,
                        status_forcelist = [500, 502, 503, 504],
                        method_whitelist = frozenset(['GET', 'POST']),
                        raise_on_status = False)
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
    
    def get_credentials(self):
         cred = OAuth2Credentials(access_token= self.access_token,
                           client_id = self.client_id,
                           client_secret= self.client_secret,
                           refresh_token= self.refresh_token,
                           token_expiry= self.token_expiry,
                           token_uri=self.token_uri,
                           user_agent = '')
         
         return cred

# a = Authorize(scope ='https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly',token_file="token.yaml", secrets_file='secret_kai.json')
# a.authorize()


'''
in the token yaml file
access_token: the token that your application sends to authorize a Google API request
expires_in:  The remaining lifetime of the access token in secondsrefresh_token: A token tha tyou can use to obtain a new access token., Refresh tokens are valid until the 
              user revokes access. Again, this field is only present in this response if you set the access_type 
                parameter to offline in the initial request to Google's authorization server
scope: the scopes of access granted by the access_token expressed as a list of space limited, case-sensitive strings
token_type: the type of token returned. At this time, this field's value is always set to Bearer'''