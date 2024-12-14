import streamlit as st  #+ sidebar
import pandas as pd
import numpy as np
import requests



st.title('Transport price predict 2') # +session state 

file_upload = st.file_uploader(label = 'Upload_csv')
process_file = st.button(label="Process_file")

if process_file:
    result = requests.post('http://localhost:8000/list_predict', json = pd.read_csv(file_upload).to_dict(orient='list'))
    result_csv = pd.DataFrame(result.json()).to_csv(index=False)

    
    st.download_button(label='Download_csv', data=result_csv, file_name='predict.csv')

   

