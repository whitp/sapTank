import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates
import pyodbc

st.title('Sap Tank Monitor')

server = st.secrets["db_server"]
database = st.secrets["db_name"]
username = st.secrets["db_username"] 
password = st.secrets["db_password"]  
driver= '{ODBC Driver 17 for SQL Server}'


@st.cache
def load_data():
    with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
        sql = "SELECT published_at, device_id, temperature, volume FROM sapdata"
        data = pd.read_sql(sql,conn)
        return data


data = load_data()

data = data.sort_values(by=['published_at'])

times = data['published_at'].to_numpy()
times = matplotlib.dates.date2num(times)
temps = data['temperature'].to_numpy()
temps = temps * 1.8 + 32
volumes = data['volume'].to_numpy()
volumes = volumes - 21

color = 'g'

st.subheader('Current Volume')
#st.text(volumes[-1])
if st.button('Reload Data'):
    st.legacy_caching.clear_cache()
    
#plot volume data
fig2, ax3 = plt.subplots()
lns3 = ax3.plot(times, volumes, color, label = 'Volume')
ax3.set_xlabel('Time')
ax3.set_ylabel('Volume (gallons)')
ax3.set_ylim(bottom = 0,top = None, auto = True)
ax3.set_xticklabels(ax3.get_xticks(), rotation = 90)

labs1 = [l.get_label() for l in lns3]
ax3.legend(lns3, labs1, loc=0)

st.pyplot(fig2)

#plot combined temperature and volume data
st.subheader('Chart')
fig, ax = plt.subplots()
lns1 = ax.plot(times, volumes, color, label = 'Volume')
ax.set_xlabel('Time')
ax.set_ylabel('Volume (gallons)')
ax.set_ylim(0,500)
ax.set_xticklabels(ax.get_xticks(), rotation = 90)


ax2 = ax.twinx()
ax2.set_ylabel('Temperature (F)')
lns2 = ax2.plot(times, temps, label = 'Temperature')

lns = lns1 + lns2
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc=0)

st.pyplot(fig)

