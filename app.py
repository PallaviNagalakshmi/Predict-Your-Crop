from flask import Flask, request, render_template
import numpy as np
import pickle
import json
import requests
from datetime import datetime

app = Flask(__name__)

# Load the model and scalers
model = pickle.load(open('model.pkl', 'rb'))
sc = pickle.load(open('standscaler.pkl', 'rb'))
mx = pickle.load(open('minmaxscaler.pkl', 'rb'))
label_encoder = pickle.load(open('labelencoder.pkl', 'rb'))

# Load crop details from JSON file
with open("crop_details.json", 'r') as file:
    crop_details = json.load(file)

def get_soil_data(poly_id, api_key):
    url = f"http://api.agromonitoring.com/agro/1.0/soil?polyid={poly_id}&appid={api_key}"
    response = requests.get(url)
    
    # Log API response status and content
    print(f"API Response Status Code: {response.status_code}")
    print(f"API Response Content: {response.content.decode('utf-8')}")
    
    # Return JSON response if status code is 200, otherwise return an empty dict
    if response.status_code == 200:
        return response.json()
    else:
        return {}

def get_weather_forecast(api_key, lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        weather = {
            'description': data['weather'][0]['description'],
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'date_time': datetime.fromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')
        }
        return weather
    else:
        return None

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/predict", methods=['POST'])
def predict():
    try:
        N = float(request.form['Nitrogen'])
        P = float(request.form['Phosphorus'])
        K = float(request.form['Potassium'])
        ph = float(request.form['pH'])
        rainfall = float(request.form['Rainfall'])
        lat = float(request.form['Latitude'])
        lon = float(request.form['Longitude'])
        
        soil_api_key = '24426d1fcabbc4e5b4db7fff4fd34762'  # Replace with your AgroMonitoring API key
        poly_id = '666a78a17fc9dcc579772c6a'  # Replace with your actual polygon ID
        soil_data = get_soil_data(poly_id, soil_api_key)

        # Debugging: Print soil data to the console
        print("Soil Data Response:", json.dumps(soil_data, indent=4))

        # Ensure the soil data contains the required keys
        if 't0' in soil_data and 'moisture' in soil_data and 't10' in soil_data:
            temp_surface = soil_data['t0']
            moisture = soil_data['moisture']
            temp_10cm = soil_data['t10']
        else:
            # Handle cases where the keys are missing
            print("Soil data does not contain required keys.")
            temp_surface = None
            moisture = None
            temp_10cm = None

        if temp_surface is not None and moisture is not None and temp_10cm is not None:
            # Fetch weather forecast data
            weather_api_key ='24426d1fcabbc4e5b4db7fff4fd34762'# Replace with your OpenWeatherMap API key
            weather_data = get_weather_forecast(weather_api_key, lat, lon)

            if weather_data:
                feature_list = [N, P, K, temp_surface, moisture, ph, rainfall]
                single_pred = np.array(feature_list).reshape(1, -1)

                mx_features = mx.transform(single_pred)
                sc_mx_features = sc.transform(mx_features)
                
                prediction = model.predict(sc_mx_features)
                predicted_label = label_encoder.inverse_transform(prediction)

                result = predicted_label[0]
                crop_detail = crop_details.get(result, {})
            else:
                result = "Unable to retrieve weather forecast data"
                crop_detail = {}
                weather_data = {}

        else:
            result = "Unable to retrieve soil data for prediction"
            crop_detail = {}
            soil_data = {}
            weather_data = {}

    except Exception as e:
        result = f"An error occurred: {e}"
        crop_detail = {}
        soil_data = {}
        weather_data = {}

    return render_template('recommendation.html', result=result, input_values=request.form, crop_detail=crop_detail, soil_data=soil_data, weather_data=weather_data)

if __name__ == "__main__":
    app.run(debug=True)
