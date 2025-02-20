import requests
import json

# TFL API endpoint for tube stations
url = "https://api.tfl.gov.uk/StopPoint/Mode/tube"

def get_zone(station):
    """
    Extracts the zone information from a station's additionalProperties.
    Looks for any property whose key contains 'zone' (case-insensitive) and returns its value.
    """
    for prop in station.get("additionalProperties", []):
        key = prop.get("key", "").lower()
        value = prop.get("value", "")
        if "zone" in key:
            return value
    return None

def get_station_lines(station):
    """
    Returns a list of line names that serve the station.
    First checks if the station object already has a 'lines' property.
    If not, it fetches detailed station data from the TFL API.
    """
    if "lines" in station:
        return [line.get("name") for line in station["lines"]]
    
    station_id = station.get("id")
    if not station_id:
        return []
    
    detail_url = f"https://api.tfl.gov.uk/StopPoint/{station_id}"
    response = requests.get(detail_url)
    if response.status_code == 200:
        data = response.json()
        return [line.get("name") for line in data.get("lines", [])]
    return []

def get_station_info(station):
    """
    Returns a dictionary with the station's name, lines, zone, and coordinates.
    """
    info = {
        "name": station.get("commonName"),
        "lines": get_station_lines(station),
        "zone": get_zone(station),
        "lat": station.get("lat"),
        "lon": station.get("lon")
    }
    return info

def fetch_stations():
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("Response type:", type(data))
        print("Response keys:", data.keys() if isinstance(data, dict) else "Data is not a dictionary")
        
        # Extract station list from the 'stopPoints' key
        stations_list = data.get("stopPoints", data)
        
        # Filter for only Zone 1 stations (where zone value equals "1")
        zone1_stations = [station for station in stations_list if get_zone(station) == "1"]
        
        # Deduplicate stations using a unique identifier (e.g., 'id')
        unique_stations = {}
        for station in zone1_stations:
            station_id = station.get("id")
            if station_id not in unique_stations:
                unique_stations[station_id] = station
        zone1_stations = list(unique_stations.values())
        
        # Print sample station info
        print("\nZone 1 Stations (sample):")
        for station in zone1_stations[:5]:
            info = get_station_info(station)
            print(f"Name: {info['name']}, Lines: {info['lines']}, Zone: {info['zone']}, Coordinates: ({info['lat']}, {info['lon']})")
        
        return zone1_stations
    else:
        print("Failed to fetch station data:", response.status_code)
        return None

if __name__ == "__main__":
    stations = fetch_stations()
    if stations:
        # Save only the required information (name, lines, zone, and coordinates) to a JSON file
        stations_info = [get_station_info(station) for station in stations]
        with open("stations_zone1.json", "w") as f:
            json.dump(stations_info, f, indent=2)