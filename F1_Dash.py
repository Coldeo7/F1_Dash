import requests
import pandas as pd
import streamlit as st



# Fetch Data from API
def get_race_results(season):
    url = f"http://ergast.com/api/f1/{season}/results.json?limit=1000"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_race_schedule(season):
    url = f"http://ergast.com/api/f1/{season}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_race_names(schedule_data):
    races = schedule_data['MRData']['RaceTable']['Races']
    race_names = {race['round']: race['raceName'] for race in races}
    return race_names


def get_all_drivers(season):
    url = f"http://ergast.com/api/f1/{season}/drivers.json"
    response = requests.get(url)
    if response.status_code == 200:
        drivers = response.json()['MRData']['DriverTable']['Drivers']
        driver_names = {driver['driverId']: f"{driver['givenName']} {driver['familyName']}" for driver in drivers}
        return driver_names
    else:
        return None


def get_all_constructors(season):
    url = f"http://ergast.com/api/f1/{season}/constructors.json"
    response = requests.get(url)
    if response.status_code == 200:
        constructors = response.json()['MRData']['ConstructorTable']['Constructors']
        constructor_names = {constructor['constructorId']: constructor['name'] for constructor in constructors}
        return constructor_names
    else:
        return None


# Process Data
def process_race_data(race_data):
    races = race_data['MRData']['RaceTable']['Races']
    processed_data = []
    for race in races:
        for result in race['Results']:
            processed_data.append({
                'race_name': race['raceName'],
                'round': race['round'],
                'driver': f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                'constructor': result['Constructor']['name'],
                'position': result['position'],
                'points': result['points']
            })
    return pd.DataFrame(processed_data)


def filter_by_driver(data, driver_name):
    return data[data['driver'] == driver_name]


def filter_by_constructor(data, constructor_name):
    return data[data['constructor'] == constructor_name]


# Streamlit App
st.title('Formula 1 Dashboard')

# Select Season
season = st.number_input('Enter the season year:', min_value=1950, max_value=2024, value=2024, step=1)

# Fetch and display schedule
schedule_data = get_race_schedule(season)
if schedule_data:
    race_names = get_race_names(schedule_data)
    drivers = get_all_drivers(season)
    constructors = get_all_constructors(season)

    # Options to select what to display
    option = st.selectbox('Choose an option', ['Race Results', 'Driver Record', 'Constructor Record'])

    race_data = get_race_results(season)
    if race_data:
        df = process_race_data(race_data)

        if option == 'Race Results':
            selected_round = st.selectbox('Select a race:', list(race_names.keys()),
                                          format_func=lambda x: race_names[x])
            if selected_round:
                round_df = df[df['round'] == str(selected_round)]
                st.write(f"### Race Results for {race_names[selected_round]}")
                st.dataframe(round_df)

        elif option == 'Driver Record':
            selected_driver = st.selectbox('Select a driver:', list(drivers.values()))
            if selected_driver:
                filtered_df = filter_by_driver(df, selected_driver)
                st.write(f"### Season Record for {selected_driver}")
                st.dataframe(filtered_df)

        elif option == 'Constructor Record':
            selected_constructor = st.selectbox('Select a constructor:', list(constructors.values()))
            if selected_constructor:
                filtered_df = filter_by_constructor(df, selected_constructor)
                st.write(f"### Season Record for {selected_constructor}")
                st.dataframe(filtered_df)
    else:
        st.error("Failed to fetch race results.")
else:
    st.error("Failed to fetch race schedule.")