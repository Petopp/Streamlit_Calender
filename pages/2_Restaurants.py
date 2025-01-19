import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

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


if 'dataCSV' in st.session_state:
    del st.session_state["dataCSV"]

if 'data' in st.session_state:
    del st.session_state["data"]

if 'Termine' in st.session_state:
    del st.session_state["Termine"]
    
if 'name_content' not in st.session_state:  
    st.session_state.name_content = '' 

if 'street_content' not in st.session_state:
    st.session_state.street_content = ''

if 'website_content' not in st.session_state:
    st.session_state.website_content = ''
      

def get_name_input():
    st.session_state.name_content = st.session_state.get("name")

def get_street_input():
    st.session_state.street_content = st.session_state.get("street")

def get_website_input():
    st.session_state.website_content = st.session_state.get("website")


def restaurant_form():
    
    
    with st.container(key='restaurant_form',border=1):
        st.header("Restaurant:")
        
        st.text_input("Name des Restaurants",autocomplete="off",key='name',value=st.session_state.name_content,on_change=get_name_input)
        st.text_input("Adresse",autocomplete="off",key='street',value=st.session_state.street_content,on_change=get_street_input)
        st.text_input("Webseite",autocomplete="off",key='website',value = st.session_state.website_content,on_change=get_website_input)
      
        
        if st.button(label='Speichern'):
            
            # prüfen ob alle felder bis auf webseite ausgefüllt sind
            if st.session_state.name_content == '' or st.session_state.street_content == '' :
                st.error("Bitte füllen Sie alle Felder aus")
                return
            
            # Abspeichern der Daten in einer CSV Liste
            with open('restaurants.csv', 'a', encoding='utf-8') as f:
                f.write(f"{st.session_state.name_content};{st.session_state.street_content};{st.session_state.website_content};""\n")
            
            
            st.session_state.clear()
            st.session_state.name_content = '' 
            st.session_state.street_content = ''
            st.session_state.website_content = ''
            st.rerun()
            
        


def view_saved_data():
    with st.container(key='restaurant_list',border=1):
        st.header("Gespeicherte Restaurants")
        try:
            st.session_state.df = pd.read_csv('restaurants.csv', encoding='utf-8', delimiter=';', names=["Name", "Adresse","Webseite", "Zuletzt besucht"])
            
            st.dataframe(st.session_state.df, hide_index=True)
            
            selected_rows = st.multiselect(
                "Wählen Sie die zu löschenden Zeilen aus:",
                st.session_state.df.index,
                format_func=lambda x: f"{st.session_state.df.iloc[x]['Name']} - {st.session_state.df.iloc[x]['Adresse']}"
            )
            
            
            
            if st.button("Löschen"):
                if selected_rows:
                    st.session_state.df.drop(selected_rows, inplace=True)
                    st.session_state.df.to_csv('restaurants.csv', sep=';', index=False, header=False, encoding='utf-8')
                    st.rerun()
                else:
                    st.warning("Bitte wählen Sie mindestens eine Zeile zum Löschen aus.")
                
        except FileNotFoundError:
            st.error("Keine gespeicherten Daten gefunden.")


restaurant_form()
view_saved_data()


