import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates
import pyodbc
import pytz

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

def showRawData(data):
    st.subheader('Raw data')
    st.write(data)

def plotAll(volumes, temps, times):
    color = 'g'

    if st.button('Reload Data'):
        st.legacy_caching.clear_cache()
        
    #plot volume data
    st.subheader('Volume Over Last 48 Hours')
    fig2, ax3 = plt.subplots()
    lns3 = ax3.plot(times[-576:-1], volumes[-576:-1], color, label = 'Volume')
    ax3.set_xlabel('Time')
    ax3.set_ylabel('Volume (gallons)')
    ax3.set_ylim(bottom = -10,top = None, auto = True)
    ax3.set_xticklabels(ax3.get_xticks(), rotation = 90)

    labs1 = [l.get_label() for l in lns3]
    ax3.legend(lns3, labs1, loc=0)
    plt.title("Last 48 Hours")
    st.pyplot(fig2)

    #plot combined temperature and volume data
    st.subheader('All Data')
    fig, ax = plt.subplots()
    lns1 = ax.plot(times, volumes, color, label = 'Volume')
    ax.set_xlabel('Time')
    ax.set_ylabel('Volume (gallons)')
    ax.set_ylim(-10,500)
    ax.set_xticklabels(ax.get_xticks(), rotation = 90)


    ax2 = ax.twinx()
    ax2.set_ylabel('Temperature (F)')
    lns2 = ax2.plot(times, temps, label = 'Temperature')

    lns = lns1 + lns2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0)

    st.pyplot(fig)

def displayStats(time, temp, temp_delta, volume, vol_delta, flow_rate, flow_delta):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Last Measurement Time", time)
    col2.metric("Temperature", "{0:8.2f} °F".format(temp), "{0:8.2f} °F".format(temp_delta))
    col3.metric("Volume", "{0:8.1f} gal".format(volume), "{0:8.1f} gal".format(vol_delta))
    col4.metric("Flow Rate", "{0:8.1f} gal/Hour".format(flow_rate), "{0:8.1f} gal/Hour".format(flow_delta))

def main():
    data = load_data()
    data = data.sort_values(by=['published_at'])
    data = data.iloc[0:-1]

    times = data['published_at'].to_numpy()

    #Extract and format temperature data
    temps = data['temperature']
    temps = temps * 1.8 + 32 #convert from C to F
    sel_temps = temps;
    temps = temps.to_numpy()

    #Extract and format volume data
    volumes = data['volume']
    volumes = volumes.rolling(5).mean()
    volumes = volumes - 21
    sel_volumes = volumes
    volumes = volumes.to_numpy()

    current_time = np.datetime_as_string(times[-1], unit='s',timezone=pytz.timezone('US/Eastern')).split("T")[1]
    displayStats(current_time, 
        temps[-1],  temps[-1]-temps[-2],
        volumes[-1], volumes[-1]-volumes[-2],
        volumes[-1]-volumes[-6]*2,volumes[-6]-volumes[-11]*2)

    plotAll(volumes, temps, times)

    #showRawData(data)


if __name__ == "__main__":
    main()