import requests

def fetch_live_soil_data(lat: float, lon: float):
    """
    Fetches live topsoil pH from the ISRIC SoilGrids Global API based on GPS coordinates.
    Since this is an Open API, NO api key is required!
    """
    url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    
    # We specify we want 'phh2o' (Soil pH in water) at a depth of 0-5cm (Topsoil)
    params = {
        "lon": lon,
        "lat": lat,
        "property": "phh2o",  
        "depth": "0-5cm",     
        "value": "mean"       
    }
    
    print(f"[Soil] Fetching live soil data for coordinates: {lat}, {lon}...")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # ISRIC returns pH multiplied by 10 (e.g., 65 means pH 6.5)
            # We dig into the JSON response to grab the exact mean value and divide by 10
            try:
                raw_ph = data['properties']['layers'][0]['depths'][0]['values']['mean']
                if raw_ph is None:
                    return {"success": False, "error": "Soil pH value is null for this location. Using fallback."}
                actual_ph = raw_ph / 10.0
                
                return {
                    "success": True,
                    "soil_ph": actual_ph,
                    "source": "ISRIC SoilGrids"
                }
            except (KeyError, IndexError):
                return {"success": False, "error": "No soil data found for this specific location (might be in the ocean)."}
        else:
            return {"success": False, "error": f"API Error {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Connection Failed: {str(e)}"}

# --- Quick Test Block ---
# If you run this file directly, it will test the API using Delhi's coordinates!
if __name__ == "__main__":
    test_lat = 28.6139
    test_lon = 77.2090
    result = fetch_live_soil_data(test_lat, test_lon)
    print("🎯 Result:", result)
