import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import os


# Daten löschen aus Temp
if 'dataCSV' in st.session_state:
    del st.session_state["dataCSV"]

if 'data' in st.session_state:
    del st.session_state["data"]

if 'Termine' in st.session_state:
    del st.session_state["Termine"]
    

def load_restaurants_csv(filepath):
    daten=pd.read_csv(filepath, delimiter=';', encoding='utf-8', header=None)
    daten_org=daten.copy()
    alt=[]
    
    for i in range(len(daten)):
        datum = daten.iloc[i,3] # dd.mm.yyyy
        
        if str(datum) == 'nan':
            continue
        
        # Datum in datetime umwandeln
        datum = datetime.strptime(datum, '%d.%m.%Y')
        
        # Datum älter als drei Jahre, dann aus liste löschen
        if datum > datetime.now() - timedelta(days=3*365):
            alt.append(i)
    
    daten.drop(alt, inplace=True)
    
    # Wenn keine Daten sortieren
    if len(daten) == 0:
        daten=daten_org.copy()
    
    return daten


def Restaurant_Suchen(Speichern=True):
    # Daten aus CSV-Datei laden restaurants.csv 
    restaurants_df = load_restaurants_csv('restaurants.csv')

    # CSV-Datei laden
    df = pd.read_csv('änderungen.csv')

    # Gruppieren nach Datum und prüfen, ob alle Werte True sind und es genau fünf Einträge gibt
    grouped = df.groupby('Datum').agg({'Wert': 'sum', 'Name': 'count'})
    available_dates = grouped[(grouped['Wert'] == 5) & (grouped['Name'] == 5)].index.tolist()

    # Bereinige die Datumswerte, um zusätzliche Informationen zu entfernen
    available_dates = [date.split(' ')[0] for date in available_dates]

    # Konvertiere die bereinigten Datumswerte in Datumsobjekte
    available_dates = pd.to_datetime(available_dates, format='%d.%m.%Y', dayfirst=True)

    # Termine nach Datum sortieren
    available_dates = available_dates.sort_values()

    # Nur ein Termin pro Monat und ignoriere Termine, die weniger als 5 Tage von heute entfernt sind
    unique_dates = []
    seen_months = set()
    today = datetime.now()
    
    # Lese besucht.csv, falls vorhanden und nicht leer
    if os.path.exists('besucht.csv') and os.path.getsize('besucht.csv') > 0:
        besucht = pd.read_csv('besucht.csv', sep=';', encoding='utf-8', header=None)
        besucht.columns = ['Datum', 'Restaurant']
        besucht['Datum'] = besucht['Datum'].str.split('(').str[0].str.strip()
        besucht['Datum'] = pd.to_datetime(besucht['Datum'], format='%d.%m.%Y', dayfirst=True, errors='coerce')
        besucht = besucht.dropna(subset=['Datum'])  # Entferne Zeilen mit NaT-Werten
    else:
        besucht = pd.DataFrame(columns=['Datum', 'Restaurant'])


    for date in available_dates:
        if (date - today).days >= 5:
            month = date.strftime('%Y-%m')  # Extrahiere Jahr und Monat
            if month not in seen_months:
                # Prüfe, ob im selben Monat und Jahr bereits ein Besuch verzeichnet ist
                try:
                    if not ((besucht['Datum'].dt.year == date.year) & (besucht['Datum'].dt.month == date.month)).any():
                        unique_dates.append(date)
                        seen_months.add(month)
                except:
                    unique_dates.append(date)
                    seen_months.add(month)
                    
    # Sortiere die einzigartigen Termine nach dem nächsten Termin
    unique_dates.sort()

    if unique_dates:
        print("Termine, an denen alle Zeit haben:")
        
        Durchlauf=0
        Liste=[]
        
        for date in unique_dates:
            
            Durchlauf+=1
            Datum=date.strftime('%d.%m.%Y (%A)')
            
            # Zufallszahl
            rN=random.randint(0,len(restaurants_df)-1)
            
            Rest=restaurants_df.iloc[rN,0]
            Adresse=restaurants_df.iloc[rN,1]
            Webseite=restaurants_df.iloc[rN,2]
            
            # Eintrag entfernen
            try:
                restaurants_df.drop(rN, inplace=True)
            except:
                pass
            
            Liste.append([Datum,Rest,Adresse,Webseite])
            
        # Daten in CSV-Datei speichern
        
        if Speichern is True:
            data=pd.DataFrame(Liste,columns=['Datum','Restaurant','Adresse','Webseite'])
            data.to_csv('auswahl.csv',index=False,sep=';',encoding='utf-8')
        
        return Liste    
                
    else:
        if os.path.exists('auswahl.csv') and Speichern is True:
            os.remove('auswahl.csv')

        return None
    

def restaurant_visited(restaurant, datum):
    # Das Datum in einer CSV Datei anfügen
    data = pd.DataFrame({'Datum': [datum], 'Restaurant': [restaurant]})
    data.to_csv('besucht.csv', mode='a', index=False, header=False, sep=';', encoding='utf-8')
    
    # Das Restaurant in der restaurants.csv suchen und dann in der letzten Spalte das Datum eintragen
    restaurants_df = pd.read_csv('restaurants.csv', delimiter=';', encoding='utf-8', header=None)
    
    for index, row in restaurants_df.iterrows():
        if row[0] == restaurant:
            restaurants_df.at[index, 3] = datum[:10]
            break
    
    restaurants_df.to_csv('restaurants.csv', index=False, header=False, sep=';', encoding='utf-8')

    st.rerun()

    
# Wenn Datei existiert
if os.path.exists('auswahl.csv'):
    
    df = pd.read_csv('auswahl.csv',sep=';',encoding='utf-8')
    
    df['Datum_only'] = df['Datum'].str.split('(').str[0].str.strip()
    df['Datum_only'] = pd.to_datetime(df['Datum_only'], format='%d.%m.%Y', dayfirst=True)
    df['ist_vergangen'] = df['Datum_only'] < pd.Timestamp.today()
    df = df[~df['ist_vergangen']]
    
    Sys_Liste=Restaurant_Suchen(False)
    
    # Prüfe in jederzeile von DF in der Spalte Datum ob der Wert in Sys_Liste enthalten ist
    # Wenn nicht, dann lösche die Zeile
    try:
        for index, row in df.iterrows():
            if row['Datum'] not in [x[0] for x in Sys_Liste]:
                df.drop(index, inplace=True)
    except:
        pass
    
    # Prüfe ob in der Sys_List ein Moat vorhanden ist der nicht in der DF vorhanden ist
    # Wenn ja, dann füge diesen hinzu
    try:
        for x in Sys_Liste:
            if x[0] not in df['Datum'].values:
                #df = df.append({'Datum': x[0], 'Restaurant': x[1], 'Adresse': x[2], 'Webseite': x[3]}, ignore_index=True)
                df_new = pd.DataFrame({'Datum': [x[0]], 'Restaurant': [x[1]], 'Adresse': [x[2]], 'Webseite': [x[3]]})
                df = pd.concat([df, df_new], ignore_index=True)

    
        data=pd.DataFrame(df,columns=['Datum','Restaurant','Adresse','Webseite'])
        data.to_csv('auswahl.csv',index=False,sep=';',encoding='utf-8')
    except:
        pass

# Wenn noch keine Datei existiert
else:
    df=Restaurant_Suchen(True)


# Sortieren nach Datum von DF
df['Datum'] = df['Datum'].str.replace(r'\s*\(.*\)$', '', regex=True)
df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', dayfirst=True)
df.sort_values(by='Datum', inplace=True)


# Lader der besucht.csv hat kein header und ist mit ; getrennt
if os.path.exists('besucht.csv') and os.path.getsize('besucht.csv') > 0:
    try:
        besucht = pd.read_csv('besucht.csv', sep=';', encoding='utf-8', header=None)
        besucht.columns = ['Datum', 'Restaurant']
        besucht['Datum'] = pd.to_datetime(besucht['Datum'], format='%d.%m.%Y', dayfirst=True, errors='coerce')
        besucht = besucht.dropna(subset=['Datum'])  # Entferne Zeilen mit NaT-Werten
    except:
        besucht = pd.DataFrame()
else:
    besucht = pd.DataFrame()



# Darstellen
for index, row in df.iterrows():
    
    with st.container(key="Viewer"+str(index), border=1):
    
        st.subheader("Termin:")
        
        
        # Convert Datum in dd.MM.yyyy
        row['Datum'] = row['Datum'].strftime('%d.%m.%Y (%A)')
        
        
        st.write(f"Am {row['Datum']} um 19:00 Uhr")
        
        st.subheader("Restaurant:")
        st.write(f"{row['Restaurant']}")
        st.write(f"{row['Adresse']}")
        st.write(f"{row['Webseite']}")
        
        Anzeigen=True
        
        for i in range(len(besucht)):
            if str(row['Restaurant']) == str(besucht.iloc[i,1]) and str(row['Datum']) == str(besucht.iloc[i,0]):
                Anzeigen=False
                break
        
        if Anzeigen is True:
            if st.button("Dort gewesen", key="botto"+str(index)):
                restaurant_visited(row['Restaurant'], row['Datum'])
        else:
            st.write("✔")




