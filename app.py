# This file actually add the pages in and manage the code

import streamlit as st

from multipage import MultiPage
from pages import mainPage, data, analytics, reporting # import your pages here
# This is for testing scripts
from pages import script2
from pages import script3
# from pages import testing
from pages import script1
from pages import script4
from pages import script23
# Page config settings
st.set_page_config(page_title='AMA Data Extraction')

#Side bar settings

# Create an instance of the app
app = MultiPage()

# Title of the main page
st.title("JELLYSMACK X AMA DATA ACQUISITION TOOL")

# Add all your application (pages) here
app.add_page("Main Page", mainPage.app)
app.add_page("PUBLIC (Data V3 API)", data.app)
app.add_page("PRIVATE (Analytics API)", analytics.app)
app.add_page("CATEGORIZATION/RETENTION PERFORMANCE ANALYSIS", script23.app)
# app.add_page("Reporting API", reporting.app)
app.add_page("SCRIPT 2", script2.app)
app.add_page("Retention Performance", script3.app)
# app.add_page("scratch", testing.app)
app.add_page("script1", script1.app)
app.add_page("DROP OFF ANALYSIS", script4.app)
# The main app
app.run()