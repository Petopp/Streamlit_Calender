import streamlit as st
from datetime import datetime, timedelta

# DEV hide
st.markdown(
    r"""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    header { visibility: hidden; }
        .css-18e3th9 { visibility: hidden; }
        .css-1d391kg { padding-top: 0px; }


        
    [data-testid="stBottom"] > div {
        background: transparent;
        }
    
    }
   

    </style>
    """, unsafe_allow_html=True
)

def download_all_csv():
    csv_files = ["restaurants.csv", "besucht.csv", "auswahl.csv", "änderungen.csv"]
    for file in csv_files:
        with open(file, "rb") as f:
            st.download_button(f"Download {file}", f, file_name=file)

download_all_csv()