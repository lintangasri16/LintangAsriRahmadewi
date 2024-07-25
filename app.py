import streamlit as st
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import sqlite3

# Load the pre-trained model
model = joblib.load('model.pkl')

# Create a numerical transformer pipeline
numerical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())
])

# Create the database table if it does not exist
def create_table():
    conn = sqlite3.connect('predictions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (id INTEGER PRIMARY KEY,
                  year INTEGER,
                  mileage REAL,
                  tax REAL,
                  mpg REAL,
                  engineSize REAL,
                  predicted_price REAL)''')
    conn.commit()
    conn.close()
create_table()

# Global variable to store prediction history
prediction_history = []

# Function to predict values
def ValuePredictor(to_predict_list):
    try:
        # Convert the input list to DataFrame
        to_predict = pd.DataFrame([to_predict_list], columns=['year', 'mileage', 'tax', 'mpg', 'engineSize'])
        
        # Apply the same preprocessing
        to_predict = numerical_transformer.transform(to_predict)
        
        # Predict using the model
        result = model.predict(to_predict)
        return result[0]
    except Exception as e:
        st.error(e)
        return None
    
# Function to save prediction to database
def save_prediction_to_db(year, mileage, tax, mpg, engineSize, predicted_price):
    conn = sqlite3.connect('predictions.db')
    c = conn.cursor()
    c.execute("INSERT INTO predictions (year, mileage, tax, mpg, engineSize, predicted_price) VALUES (?, ?, ?, ?, ?, ?)",
              (year, mileage, tax, mpg, engineSize, predicted_price))
    conn.commit()
    conn.close()

# Streamlit interface
st.title('Prediksi Harga Mobil Audi')

# Input form
with st.form("prediction_form"):
    year = st.number_input('Tahun', min_value=1990, max_value=2023, value=2020)
    mileage = st.number_input('Jarak Tempuh (miles)', value=10000)
    tax = st.number_input('Pajak (£)', value=150)
    mpg = st.number_input('Konsumsi BBM (mpg)', value=30.0)
    engineSize = st.number_input('Ukuran Mesin (L)', value=2.0)
    submit = st.form_submit_button("Prediksi")

if submit:
    to_predict_list = [year, mileage, tax, mpg, engineSize]
    result = ValuePredictor(to_predict_list)
    
    if result is not None:
        # Save prediction result to database
        save_prediction_to_db(year, mileage, tax, mpg, engineSize, result)
        prediction_history.append({
            'year': year,
            'mileage': mileage,
            'tax': tax,
            'mpg': mpg,
            'engineSize': engineSize,
            'predicted_price': result
        })
        st.success(f'Harga yang diprediksi: £ {result}')
    else:
        st.error('Error dalam prediksi')

# Show recent predictions
st.subheader('10 Data Terbaru')
recent_data = mobil_data.tail(10).to_dict(orient='records')
for record in prediction_history:
    recent_data.append({
        'year': record['year'],
        'mileage': record['mileage'],
        'tax': record['tax'],
        'mpg': record['mpg'],
        'engineSize': record['engineSize'],
        'predicted_price': record['predicted_price']
    })
df = pd.DataFrame(recent_data)
st.write(df)
