import requests

api_key = "24426d1fcabbc4e5b4db7fff4fd34762"  # Replace with your AgroMonitoring API key
polygon_name = "cantilever"  # Replace with the name of your polygon

def get_polygon_id(api_key, polygon_name):
    url = f"http://api.agromonitoring.com/agro/1.0/polygons?appid={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        if response.status_code == 200:
            polygons = response.json()

            for polygon in polygons:
                if polygon['name'] == polygon_name:
                    return polygon['id']
            
            print(f"Polygon with name '{polygon_name}' not found.")
            return None
        else:
            print(f"Failed to retrieve polygons. Status Code: {response.status_code}")
            print(f"Response Content: {response.content.decode('utf-8')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving polygons: {e}")
        return None

# Usage example
polygon_id = get_polygon_id(api_key, polygon_name)
if polygon_id:
    print(f"Found Polygon ID: {polygon_id}")
else:
    print("Failed to retrieve Polygon ID.")
