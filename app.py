# This file actually add the pages in and manage the code

import streamlit as st

from multipage import MultiPage
from pages import mainPage, data, analytics, reporting # import your pages here


# Page config settings
st.set_page_config(page_title='AMA Data Extraction')

#Side bar settings

# Create an instance of the app
app = MultiPage()

# Title of the main page
st.title("AMA Extractor Tool")

# Add all your application (pages) here
app.add_page("Main Page", mainPage.app)
app.add_page("Data V3 API", data.app)
app.add_page("Analytics API", analytics.app)
app.add_page("Reporting API", reporting.app)



# The main app
app.run()