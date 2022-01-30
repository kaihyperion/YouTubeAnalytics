import os
import secrets
import requests
from requests.adapters import HTTPAdapter
from requests_oauthlib import OAuth2Session #https://docs.authlib.org/en/latest/client/oauth2.html
from urllib3.util.retry import Retry
from yaml import load, dump, YAMLError

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
    
    
# Google's OAUTH 2.0 endpoint url
authorization_base_url = 'https://accounts.google.com/o/oauth2/v2/auth'
token_uri = 'https://www.googleapis.com/oauth2/v4/token'

class Authorize:
    def __init__(self, scope, token_file, secrets_file):
        self.scope = scope
        self.token_file = token_file
        self.session = None
        self.token = None
        
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
        except (YAMLError, IOError):
            return None
        return token
    
    def save_token(self, token):
        with open(self.token_file, 'w') as stream:
            dump(token, stream, Dumper = Dumper)
        os.chmod(self.token_file, 0o600)
        
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


a = Authorize(scope ='https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly',token_file="token.yaml", secrets_file='secret_kai.json')
a.authorize()