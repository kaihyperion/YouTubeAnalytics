import streamlit as st
import pandas as pd

def app():
    st.title("scratch")
    a = pd.read_csv("/home/kyperion/Documents/AMA/data/mock_06.27.2022_18_58.csv")
    st.dataframe(a)
    a['RPM'] = (a['estimatedRevenue']*1000) / (a['views'])
    st.dataframe(a)
    st.table(a.groupby('content_type')['estimatedRevenue', 'views', 'subscribersGained','RPM'].mean().style.highlight_max(color='green').highlight_min(color='pink'))
    st.dataframe(a.groupby('video_length_category')['estimatedRevenue', 'views', 'subscribersGained','RPM'].mean().style.highlight_max(color='green').highlight_min(color='pink'))
