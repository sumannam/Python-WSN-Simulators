# streamlit 설치법
# [Streamlit • A faster way to build and share data apps](https://streamlit.io/)
# pip install streamlit

# streamlit run XX.py

# pygwalker 설치법 https://github.com/Kanaries/pygwalker
# pip install pygwalker

# C:\Users\user\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\streamlit run d:\git\python-wsn-simulator\data_streamlit.py\
# C:\Users\user\AppData\Roaming\Python\Python312\Scripts\streamlit run ./utils/data_streamlit.py

from pygwalker.api.streamlit import StreamlitRenderer
import pandas as pd
import streamlit as st
 
# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="Use Pygwalker In Streamlit",
    layout="wide"
)
# Import your data
df = pd.read_csv('./results/final_nodes_state.csv')
 
pyg_app = StreamlitRenderer(df)
 
pyg_app.explorer()