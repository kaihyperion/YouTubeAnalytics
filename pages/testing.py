import streamlit as st
import youtubeAnalytics
import youtubeData
import configparser
import oauth
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def app():
    st.title("CATEGORIZATION/RETENTION PERFORMANCE ANALYSIS")
    
    ###############################################################################
    # INITIALIZE CONFIGURATION
    #############################################################################
    
    config = configparser.ConfigParser()
    config.read('conf.ini')
    SCOPE = list(config.get('SCOPE Settings', 'scopelist').split(','))
    auth = oauth.Authorize(scope = SCOPE, token_file='authentications/token.yaml',
                           secrets_file= 'authentications/secret_ama2.json')
    auth.authorize()
    credentials = auth.get_credentials()
    
    ANALv2 = youtubeAnalytics.YouTubeAnalytics(credentials)
    DATAv3 = youtubeData.YouTubeData(credentials)
    ANALv2.api_build()
    DATAv3.api_build()
    
    
    #################################################################################
    # CSV UPLOAD
    #################################################################################
    if 'csv' not in st.session_state:
        ################################
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Add csv checker? so it has all the necessary column and such
        uploaded_file = st.file_uploader("CSV file here")

        if not uploaded_file:
            st.info('The CSV must contain the following columns:\n video_length (HH:MM:SS), videoIDs,content_type ')
        else:
            st.success('CSV is successfully uploaded')
            st.session_state['csv'] = pd.read_csv(uploaded_file)

            st.experimental_rerun()
    
    
    
    #################################################################################
    # Once CSV is uploaded, we grab USER INPUT
    #################################################################################
    
    if 'csv' in st.session_state:
        with st.form('user_options'):
            st.write("User Options to run")
            
            category_choice = st.multiselect(label = 'Choose how you would like to CATEGORIZE the data:',
                                            options=['length', 'content_type'])
            st.session_state['user_option'] = category_choice
            
            
            st.session_state['start'] = st.date_input("Start Date: ", value=datetime.strptime("2009-01-01", "%Y-%m-%d"))
            st.session_state['end'] = st.date_input("End Date: ")
            ANALv2.startDate = st.session_state['start']
            ANALv2.endDate = st.session_state['end']
            
            
            short_options = st.checkbox("Exclude Shorts")
            retention_flag = st.checkbox("Include Retention Data")
            submitted = st.form_submit_button("Submit")
        
        
        
    #################################################################################
    # If CSV and USER input is processed,
    #################################################################################
    
        if submitted:
            st.success('CSV is still correctly loaded')
            ANALv2.setStartDate(st.session_state['start'])
            ANALv2.setEndDate(st.session_state['end'])
            
            # First if the short exclusion is True, GET RID OF SHORTS
            if short_options:
                st.session_state['csv'] = DATAv3.short_remover(st.session_state['csv'])
            
            
            # Next, if the length option is selected,
            # Find the Length Category of videos
            col1, col2 = st.columns(2)
            if 'length' in st.session_state['user_option']:
                if 'length_in_seconds' not in st.session_state['csv']:
                    
                    #video_length_classifier will convert the session_state['csv'] to include length_category
                    st.session_state['csv'],q_array = DATAv3.video_length_classifier(st.session_state['csv'])
                    with col1:
                        st.write(st.session_state['csv']['video_length_category'].value_counts())
                    # st.write(q_array)
                    
                    with col2:
                        st.write(f"short: {int(q_array[0])} ~ {int(q_array[1])}")
                        st.write(f"medium: {int(q_array[1])} ~ {int(q_array[2])}")
                        st.write(f"long: {int(q_array[2])} ~ {int(q_array[3])}")
                else:
                    st.session_state['csv'], q_array = DATAv3.video_length_classifier(st.session_state['csv'])
                    with col1:
                        st.write(st.session_state['csv']['video_length_category'].value_counts())
                    with col2:
                        st.write(f"short: {int(q_array[0])} ~ {int(q_array[1])}")
                        st.write(f"medium: {int(q_array[1])} ~ {int(q_array[2])}")
                        st.write(f"long: {int(q_array[2])} ~ {int(q_array[3])}")


            #progress bar settings
            status_bar = st.progress(0)
            size = len(st.session_state['csv']['videoIDs'])
            status_current = 0
            
            
            # List of Video IDs we need to analyze
            # shortVideo_ID_List = newDF.loc[newDF['video_length_category'] == 'short']['videoIDs'].tolist()
            # mediumVideo_ID_List = newDF.loc[newDF['video_length_category'] == 'medium']['videoIDs'].tolist()
            # longVideo_ID_List = newDF.loc[newDF['video_length_category'] == 'long']['videoIDs'].tolist()
            