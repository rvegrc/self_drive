import streamlit as st  #+ sidebar
import pandas as pd
import numpy as np
import requests




st.title('Car coords predict') # +session state 

st.write('This is a simple web app to predict car coordinates')
# select folder with observations
select_folder = st.selectbox(label='Select folder', options=['folder1', 'folder2', 'folder3'])
st.write(f'You selected {select_folder}')


if select_folder:
    result = requests.post('http://localhost:8000/dataset_create', json={'path': select_folder})
    result_csv = pd.DataFrame(result.json()).to_csv(index=False)

    
    st.download_button(label='Download_created_dataset_in_csv', data=result_csv, file_name='dataset.csv')

   

