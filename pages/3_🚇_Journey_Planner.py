# streamlit for web design
import streamlit as st

# requests for api access
import requests

# json for processing api output
import json

# pandas for tables
import pandas as pd

# for accurate dates and times
from datetime import datetime

# for the map
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


# Load stations from CSV; fallback to a default list if there's an error.
try:
    station_df = pd.read_csv("zone1_stations.csv")
    stations = list(station_df.itertuples(index=False, name=None))
except Exception as e:
    st.error("Error loading station list: " + str(e))
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
# Create a form with searchable drop downs for station selection
with st.form("journey_form"):
    col1, col2 = st.columns(2)
    with col1:
        origin_name = st.selectbox("From", options=station_names, index=station_names.index("Westminster Underground Station"),
                                     help="Select your starting station")
    with col2:
        destination_name = st.selectbox("To", options=station_names, index=station_names.index("Bank Underground Station"),
                                        help="Select your destination station")
    submitted = st.form_submit_button("Plan Journey")


def fetch_journey(origin_id, destination_id):
    # Fetches the journey details from the TfL API.
    
    # url for the api, pass in the origin and destination ids
    url = f"https://api.tfl.gov.uk/journey/journeyresults/{origin_id}/to/{destination_id}"
    
    # get the data from the url
    response = requests.get(url)
    
    # request can be successfull or not, success code is 200
    if response.status_code == 200:
        
        # if successful we get a json dictionary
        return response.json()
    
    # if not successful, we get an error message
    else:
        st.error("Error fetching journey: " + response.text)
        return None

# api gives times in a specific format, need to convert to be more readable
# iso format: 2021-10-01T12:34:56
# we want: 12:34
def format_time(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%H:%M")
    except Exception:
        return iso_str

# Display information about a single journey leg.
def display_leg(leg):
    # Displays text of the Leg instructions and summary of the journey.
    st.markdown(f"**Leg:** {leg['instruction']['summary']}")
    dep_station = leg['departurePoint']['commonName']
    arr_station = leg['arrivalPoint']['commonName']
    leg_dep_time = format_time(leg.get("departureTime", ""))
    leg_arr_time = format_time(leg.get("arrivalTime", ""))
    st.write(f"**From:** {dep_station}  →  **To:** {arr_station}")
    st.write(f"Departure: {leg_dep_time} | Arrival: {leg_arr_time} | Duration: {leg.get('duration', '?')} minutes")
    

    # Displays a short summary of the journey in a blue Information box
    if leg['instruction'].get('detailed'):
        st.info(f"Details: {leg['instruction']['detailed']}")
    
    # Displays obstacles in the journey e.g. stairs at the station
    if leg.get("obstacles"):
        st.write("**Obstacles:**")
        for obs in leg["obstacles"]:
            st.write(f"- {obs.get('type')} ({obs.get('incline')})")
    
    # Draw a continuous path for the leg if available.
    if leg.get("path") and leg["path"].get("lineString"):
        try:
            coords = json.loads(leg["path"]["lineString"])
            # Swap [lat, lon] to [lon, lat] for Pydeck
            coords_swapped = [[c[1], c[0]] for c in coords]

            # Adds a layer on top of the map, which is a blue line of the path of the journey
            layer = pdk.Layer(
                "PathLayer",
                data=[{"path": coords_swapped}],
                get_path="path",
                get_color=[0, 128, 255, 255],  # Blue line, rgb colours
                width_scale=15,  # Width of the line
                width_min_pixels=2, # Minimum Width of the line
                get_width=5,  
                pickable=False,  # Makes the line not clickable
            )
            view_state = pdk.ViewState(
                latitude=coords_swapped[0][1],
                longitude=coords_swapped[0][0],
                zoom=12,
                pitch=0,
            )
            deck = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "Path"})
            st.pydeck_chart(deck, height=300)
        except Exception as e:
            st.write("Map unavailable: error parsing coordinates.", e)

# Display a full journey including header and its legs
def display_journey(journey, idx):
    # Gather tube line names from journey legs
    line_names = []
    for leg in journey.get("legs", []):
        if leg.get("mode", {}).get("id") == "tube" and leg.get("routeOptions"):
            
            # Puts the names of the lines used in the journey in the header of the expander box
            for route in leg["routeOptions"]:
                name = route.get("name", "").strip()
                if name and name not in line_names:
                    line_names.append(name)
    
    if line_names:
        header = f"{', '.join(line_names)} | {journey.get('duration', '?')} minutes"
    else:
        header = f"Journey {idx} | {journey.get('duration', '?')} minutes"
    
    # Expander box to display the entire journey details 
    with st.expander(header):
        start_time = format_time(journey.get("startDateTime", ""))
        arrival_time = format_time(journey.get("arrivalDateTime", ""))
        st.markdown(f"**Start:** {start_time} &nbsp;&nbsp; **Arrival:** {arrival_time}")
        
        # Gets the legs for the journey and displays them in the expander box
        for leg in journey.get("legs", []):
            display_leg(leg)

# After clicking submit button, fetch and display journey details.
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
                for idx, journey in enumerate(journeys, start=1):
                    display_journey(journey, idx)