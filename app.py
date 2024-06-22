from flask import Flask, request, render_template
import numpy as np
import pickle
import json

app = Flask(__name__)  # Corrected this line

# Load the model and scalers
model = pickle.load(open('model.pkl', 'rb'))
sc = pickle.load(open('standscaler.pkl', 'rb'))
mx = pickle.load(open('minmaxscaler.pkl', 'rb'))
label_encoder = pickle.load(open('labelencoder.pkl', 'rb'))

# Load crop details from JSON file
with open("crop_details.json", 'r') as file:
    crop_details = json.load(file)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/predict", methods=['POST'])
def predict():
    try:
        # Retrieve form data and convert to float
        N = float(request.form['Nitrogen'])
        P = float(request.form['Phosphorus'])
        K = float(request.form['Potassium'])
        temp = float(request.form['Temperature'])
        humidity = float(request.form['Humidity'])
        ph = float(request.form['pH'])
        rainfall = float(request.form['Rainfall'])

        # Create feature array
        feature_list = [N, P, K, temp, humidity, ph, rainfall]
        single_pred = np.array(feature_list).reshape(1, -1)

        # Apply MinMax scaling and Standard scaling
        mx_features = mx.transform(single_pred)
        sc_mx_features = sc.transform(mx_features)
        
        # Make prediction
        prediction = model.predict(sc_mx_features)

        # Decode the prediction
        predicted_label = label_encoder.inverse_transform(prediction)

        # Prepare the result
        result = predicted_label[0]
        
        # Get crop details based on predicted crop
        crop_detail = crop_details.get(result, {})

    except Exception as e:
        # Handle errors gracefully and return an error message
        result = f"An error occurred: {e}"
        crop_detail = {}

    return render_template('recommendation.html', result=result, input_values=request.form, crop_detail=crop_detail)

if __name__ == "__main__":  # Corrected this line
    app.run(debug=True)
