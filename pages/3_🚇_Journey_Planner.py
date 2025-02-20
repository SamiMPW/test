import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import pydeck as pdk

# Use default page style
st.set_page_config(page_title="Tube Journey Planner")
st.title("🚇 Tube Journey Planner – Zone 1 London")
st.markdown(
    """
    Plan your tube journey between Zone 1 London tube stations.
    
    Select the **From** and **To** stations below.
    
    (Note: Only tube journeys in Zone 1 are supported.)
    """
)

# Sample list of Zone 1 tube stations with their unique TfL identifiers.
stations = [
    ("Bank", "1000013"),
    ("Westminster", "1000266"),
    ("Embankment", "940GZZLUEMB"),
    ("Waterloo", "940GZZLUWLO"),
    ("Charing Cross", "940GZZLUKCX"),
    ("Leicester Square", "940GZZLULSQ"),
    ("Piccadilly Circus", "940GZZLUPIC"),
    ("Oxford Circus", "940GZZLUOXC"),
    ("Bond Street", "940GZZLUBDS"),
    ("Holborn", "940GZZLUHOB")
]

station_names = [name for name, _ in stations]
station_ids = {name: id for name, id in stations}

# Create a form with searchable drop downs for station selection.
with st.form("journey_form"):
    col1, col2 = st.columns(2)
    with col1:
        origin_name = st.selectbox("From", options=station_names, index=station_names.index("Westminster"),
                                     help="Select your starting station")
    with col2:
        destination_name = st.selectbox("To", options=station_names, index=station_names.index("Bank"),
                                        help="Select your destination station")
    submitted = st.form_submit_button("Plan Journey")

def fetch_journey(origin_id, destination_id):
    url = f"https://api.tfl.gov.uk/journey/journeyresults/{origin_id}/to/{destination_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching journey: " + response.text)
        return None

def format_time(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%H:%M")
    except Exception:
        return iso_str

if submitted:
    origin_id = station_ids[origin_name]
    destination_id = station_ids[destination_name]
    with st.spinner("Fetching journey details…"):
        data = fetch_journey(origin_id, destination_id)
        if data:
            journeys = data.get("journeys", [])
            if not journeys:
                st.error("No journeys found.")
            else:
                # For each journey, build a header showing the tube lines and total duration.
                for idx, journey in enumerate(journeys, start=1):
                    line_names = []
                    for leg in journey.get("legs", []):
                        if leg.get("mode", {}).get("id") == "tube" and leg.get("routeOptions"):
                            for route in leg["routeOptions"]:
                                name = route.get("name", "").strip()
                                if name and name not in line_names:
                                    line_names.append(name)
                    if line_names:
                        header = f"{', '.join(line_names)} | {journey.get('duration', '?')} minutes"
                    else:
                        header = f"Journey {idx} | {journey.get('duration', '?')} minutes"
                    
                    with st.expander(header):
                        start_time = format_time(journey.get("startDateTime", ""))
                        arrival_time = format_time(journey.get("arrivalDateTime", ""))
                        st.markdown(f"**Start:** {start_time} &nbsp;&nbsp; **Arrival:** {arrival_time}")
                        
                        for leg in journey.get("legs", []):
                            st.markdown(f"**Leg:** {leg['instruction']['summary']}")
                            dep_station = leg['departurePoint']['commonName']
                            arr_station = leg['arrivalPoint']['commonName']
                            leg_dep_time = format_time(leg.get("departureTime", ""))
                            leg_arr_time = format_time(leg.get("arrivalTime", ""))
                            st.write(f"**From:** {dep_station}  →  **To:** {arr_station}")
                            st.write(f"Departure: {leg_dep_time} | Arrival: {leg_arr_time} | Duration: {leg.get('duration', '?')} minutes")
                            
                            if leg['instruction'].get('detailed'):
                                st.info(f"Details: {leg['instruction']['detailed']}")
                            
                            if leg.get("obstacles"):
                                st.write("**Obstacles:**")
                                for obs in leg["obstacles"]:
                                    st.write(f"- {obs.get('type')} ({obs.get('incline')})")
                            
                            # Use Pydeck's PathLayer to draw a simple continuous line for the leg path.
                            if leg.get("path") and leg["path"].get("lineString"):
                                try:
                                    coords = json.loads(leg["path"]["lineString"])
                                    # Swap the coordinates from [lat, lon] to [lon, lat]
                                    coords_swapped = [[c[1], c[0]] for c in coords]
                                    
                                    layer = pdk.Layer(
                                        "PathLayer",
                                        data=[{"path": coords_swapped}],
                                        get_path="path",
                                        get_color=[0, 128, 255, 255],  # Blue line
                                        width_scale=20,
                                        width_min_pixels=2,
                                        get_width=5,
                                        pickable=False,
                                    )
                                    view_state = pdk.ViewState(
                                        latitude=coords_swapped[0][1],
                                        longitude=coords_swapped[0][0],
                                        zoom=12,
                                        pitch=0,
                                    )
                                    deck = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "Path"})
                                    # Specify a fixed height to avoid black gaps.
                                    st.pydeck_chart(deck, height=300)
                                except Exception as e:
                                    st.write("Map unavailable: error parsing coordinates.", e)