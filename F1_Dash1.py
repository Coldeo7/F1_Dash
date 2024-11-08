import requests
import pandas as pd
import streamlit as st

# Base URL for OpenF1 API
BASE_URL = "https://api.openf1.org/v1"

# Fetch Data from API
def get_race_schedule(season):
    url = f"{BASE_URL}/sessions?year={season}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_race_results(session_key):
    url = f"{BASE_URL}/laps?session_key={session_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_all_drivers(session_key):
    url = f"{BASE_URL}/drivers?session_key={session_key}"
    response = requests.get(url)
    if response.status_code == 200:
        drivers = response.json()
        driver_names = {driver['driver_number']: driver['full_name'] for driver in drivers}
        return driver_names
    else:
        return None

def get_all_constructors(session_key):
    url = f"{BASE_URL}/drivers?session_key={session_key}"
    response = requests.get(url)
    if response.status_code == 200:
        drivers = response.json()
        constructor_names = {driver['driver_number']: driver['team_name'] for driver in drivers}
        return constructor_names
    else:
        return None

# Process Data
def process_race_data(lap_data, drivers, constructors):
    processed_data = []
    for lap in lap_data:
        driver_number = lap['driver_number']
        processed_data.append({
            'race_name': lap.get('race_name', 'Unknown'),
            'round': lap.get('round', 'Unknown'),
            'driver': drivers.get(driver_number, 'Unknown'),
            'constructor': constructors.get(driver_number, 'Unknown'),
            'position': lap.get('position', 'N/A'),
            'points': lap.get('points', 'N/A')
        })
    return pd.DataFrame(processed_data)

def filter_by_driver(data, driver_name):
    return data[data['driver'] == driver_name]

def filter_by_constructor(data, constructor_name):
    return data[data['constructor'] == constructor_name]

# Streamlit App
st.title('Formula 1 Dashboard')

# Select Season
season = st.number_input('Enter the season year:', min_value=2018, max_value=2024, value=2024, step=1)

# Fetch and display schedule
schedule_data = get_race_schedule(season)
if schedule_data:
    meetings = schedule_data
    meeting_names = {meeting['session_key']: f"{meeting['country_name']} - {meeting['session_name']}" for meeting in meetings}

    # Options to select what to display
    option = st.selectbox('Choose an option', ['Race Results', 'Driver Record', 'Constructor Record'])

    if option == 'Race Results':
        selected_session_key = st.selectbox('Select a race:', list(meeting_names.keys()),
                                            format_func=lambda x: meeting_names[x])
        if selected_session_key:
            lap_data = get_race_results(selected_session_key)
            if lap_data:
                drivers = get_all_drivers(selected_session_key)
                constructors = get_all_constructors(selected_session_key)
                df = process_race_data(lap_data, drivers, constructors)
                st.write(f"### Race Results for {meeting_names[selected_session_key]}")
                st.dataframe(df[['race_name', 'round', 'driver', 'constructor', 'position', 'points']])
            else:
                st.error("Failed to fetch race results.")

    elif option == 'Driver Record':
        drivers = {meeting['session_key']: get_all_drivers(meeting['session_key']) for meeting in meetings}
        all_drivers = {driver for driver_dict in drivers.values() for driver in driver_dict.values()}
        selected_driver = st.selectbox('Select a driver:', list(all_drivers))
        if selected_driver:
            all_data = []
            for session_key, driver_dict in drivers.items():
                if selected_driver in driver_dict.values():
                    lap_data = get_race_results(session_key)
                    if lap_data:
                        constructors = get_all_constructors(session_key)
                        df = process_race_data(lap_data, driver_dict, constructors)
                        filtered_df = filter_by_driver(df, selected_driver)
                        all_data.append(filtered_df)
            if all_data:
                result_df = pd.concat(all_data)
                st.write(f"### Season Record for {selected_driver}")
                st.dataframe(result_df[['race_name', 'round', 'driver', 'constructor', 'position', 'points']])
            else:
                st.error("No data available for the selected driver.")

    elif option == 'Constructor Record':
        constructors = {meeting['session_key']: get_all_constructors(meeting['session_key']) for meeting in meetings}
        all_constructors = {constructor for constructor_dict in constructors.values() for constructor in constructor_dict.values()}
        selected_constructor = st.selectbox('Select a constructor:', list(all_constructors))
        if selected_constructor:
            all_data = []
            for session_key, constructor_dict in constructors.items():
                if selected_constructor in constructor_dict.values():
                    lap_data = get_race_results(session_key)
                    if lap_data:
                        drivers = get_all_drivers(session_key)
                        df = process_race_data(lap_data, drivers, constructor_dict)
                        filtered_df = filter_by_constructor(df, selected_constructor)
                        all_data.append(filtered_df)
            if all_data:
                result_df = pd.concat(all_data)
                st.write(f"### Season Record for {selected_constructor}")
                st.dataframe(result_df[['race_name', 'round', 'driver', 'constructor', 'position', 'points']])
            else:
                st.error("No data available for the selected constructor.")
else:
    st.error("Failed to fetch race schedule.")
