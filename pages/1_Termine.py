import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
    
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

if "data" not in st.session_state:

    # Generiere Datumsangaben der kommenden 300 Tage
    dates = [(datetime.today() + timedelta(days=i)).strftime('%d.%m.%Y (%A)') for i in range(300)]

    # Erstelle ein DataFrame mit den Datumsangaben und Platzhalternamen
    data = pd.DataFrame({
        'Datum': dates,
        'Katha': [False] * 300,
        'Sara': [False] * 300,
        'Christoph': [False] * 300,
        'Manuel': [False] * 300,
        'Peter': [False] * 300
    })
    
    # Speichere das DataFrame in der Session
    st.session_state.data = data


# dataCSV übertragen
if 'dataCSV' not in st.session_state:
    if os.path.exists('änderungen.csv'):
        daten = pd.read_csv('änderungen.csv')

        # Daten anpassen für änderungen_liste (datum, name, wert)
        st.session_state.dataCSV = []
        for index, row in daten.iterrows():
            st.session_state.dataCSV.append((row['Datum'], row['Name'], row['Wert']))

        # Daten in data einfügen
        for index, row in daten.iterrows():
            st.session_state.data.at[st.session_state.data[st.session_state.data['Datum'] == row['Datum']].index[0], row['Name']] = row['Wert']
    else:
        st.session_state.dataCSV = []

# Zeige die Tabelle in Streamlit an
edited_df = st.data_editor(st.session_state.data, hide_index=True, key="Termine")

# Erhalte die Änderungen
Veränderungen = st.session_state["Termine"]["edited_rows"]

änderungen_liste = []

# Liste zum Speichern der Änderungen
if 'dataCSV' in st.session_state:
    änderungen_liste = st.session_state.dataCSV.copy()

# Datum für den geänderten Index erhalten und speichern
for index in Veränderungen.keys():
    datum = st.session_state.data.at[index, 'Datum']
    for name, wert in Veränderungen[index].items():
        änderungen_liste.append((datum, name, wert))

try:
    if len(änderungen_liste) > 0:
        # Liste der zu entfernenden Einträge
        to_remove = []

        # Prüfe bei allen False Einträgen, ob es einen True Wert gibt und wenn ja, dann füge beide zur Entfernen-Liste hinzu
        for i in range(len(änderungen_liste)):
            if änderungen_liste[i][2] == False:
                for j in range(len(änderungen_liste)):
                    if (änderungen_liste[i][0] == änderungen_liste[j][0]
                        and änderungen_liste[i][1] == änderungen_liste[j][1]
                        and änderungen_liste[j][2] == True):
                        to_remove.append(i)
                        to_remove.append(j)
                        break

        # Entferne die Einträge aus der Liste
        for index in sorted(to_remove, reverse=True):
            del änderungen_liste[index]

        # Entferne alle verbleibenden False-Einträge
        änderungen_liste = [eintrag for eintrag in änderungen_liste if eintrag[2] != False]

        # Entferne Duplikate
        änderungen_liste = list(set(änderungen_liste))

        # Veränderung als CSV Speichern
        änderungen_df = pd.DataFrame(änderungen_liste, columns=['Datum', 'Name', 'Wert'])
        änderungen_df.to_csv("änderungen.csv", index=False)

except Exception as e:
    st.write(f"Error: {e}")






