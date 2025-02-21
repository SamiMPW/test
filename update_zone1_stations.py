import requests
import pandas as pd

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
        print("Error fetching data from TfL API:", e)
        return []
    
    data = response.json()
    zone1_stations = []
    
    for station in data:
        zone = None
        # Look for a property with key "Zone"
        for prop in station.get("additionalProperties", []):
            if prop.get("key") == "Zone":
                zone = prop.get("value")
                break
        
        if zone == "1":
            # Prefer the icsCode as a unique identifier, fallback to station id if not available
            station_id = station.get("icsCode") or station.get("id")
            name = station.get("commonName")
            if station_id and name:
                zone1_stations.append({"name": name, "id": station_id})
    
    return zone1_stations

def main():
    stations = fetch_zone1_stations()
    if not stations:
        print("No Zone 1 stations found or there was an error fetching the data.")
        return

    # Convert the list of dictionaries into a DataFrame and sort alphabetically by station name.
    df = pd.DataFrame(stations)
    df = df.sort_values("name")
    
    # Write the DataFrame to a CSV file.
    output_file = "zone1_stations.csv"
    try:
        df.to_csv(output_file, index=False)
        print(f"Successfully updated {output_file} with {len(df)} Zone 1 stations.")
    except Exception as e:
        print("Error writing CSV file:", e)

if __name__ == "__main__":
    main()