import streamlit as st
import requests
import pandas as pd

st.title("Update Zone 1 Stations CSV")
st.markdown(
    """
    This page fetches the latest Zone 1 tube station data from the TfL API and updates the CSV file (`zone1_stations.csv`) in the codebase.
    
    Click the button below to refresh the list of popular Zone 1 stations.
    """
)

def fetch_zone1_stations():
    """
    Fetch all tube stations from the TfL API and filter those in Zone 1.
    Returns a list of dictionaries with 'name' and 'id'.
    """
    url = "https://api.tfl.gov.uk/StopPoint/Type/NaptanMetroStation"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        st.error(f"Error fetching data from TfL API: {e}")
        return None
    
    data = response.json()
    zone1_stations = []
    
    for station in data:
        zone = None
        # Look for a property with key "Zone" in additionalProperties
        for prop in station.get("additionalProperties", []):
            if prop.get("key") == "Zone":
                zone = prop.get("value")
                break
        
        if zone == "1":
            # Prefer the icsCode as a unique identifier; fallback to the station id.
            station_id = station.get("icsCode") or station.get("id")
            name = station.get("commonName")
            if station_id and name:
                zone1_stations.append({"name": name, "id": station_id})
    
    return zone1_stations

if st.button("Update Zone 1 Stations CSV"):
    stations = fetch_zone1_stations()
    if stations is None:
        st.error("Failed to fetch stations from the API.")
    elif not stations:
        st.warning("No Zone 1 stations found.")
    else:
        # Convert the list of stations into a DataFrame and sort alphabetically.
        df = pd.DataFrame(stations)
        df = df.sort_values("name")
        try:
            df.to_csv("zone1_stations.csv", index=False)
            st.success(f"Successfully updated zone1_stations.csv with {len(df)} stations.")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error writing CSV file: {e}")