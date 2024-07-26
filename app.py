import streamlit as st
import joblib
import pickle
import numpy as np
import pandas as pd
import sqlite3

# Load the decision tree model
model = pickle.load(open('model.sav', 'rb'))

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

# Streamlit interface
st.title('Prediksi Harga Mobil Audi')

# Input data dengan contoh angka valid untuk pengujian
year = st.text_input('year')
mileage = st.text_input('mileage')
tax = st.text_input('tax')
mpg = st.text_input('mpg')
engineSize = st.text_input('engineSize')

if st.button("Prediksi"):
    try:
        # Save the data to the SQLite database
        with sqlite3.connect("predictions.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO predictions (year, mileage, tax, mpg, engineSize) VALUES (?, ?, ?, ?, ?)",
                        (year, mileage, tax, mpg, engineSize))
            con.commit()

        # Make a prediction
        to_predict_list = [float(year), float(mileage), float(tax), float(mpg), float(engineSize)]
        to_predict = np.array(to_predict_list).reshape(1, -1)
        result = model.predict(to_predict)[0]

     # Display the prediction result
        st.subheader("Prediction Result")
        st.write(f"Harga yang diprediksi: £ {result}")
        
        # Update the database with the prediction result
        with sqlite3.connect("predictions.db") as con:
            cur = con.cursor()
            cur.execute("UPDATE predictions SET predicted_price = ? WHERE year = ? AND mileage = ? AND tax = ? AND mpg = ? AND engineSize = ?",
                        (result, year, mileage, tax, mpg, engineSize))
            con.commit()
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Show recent predictions
st.subheader('Data Prediksi Terbaru')
try:
    con = sqlite3.connect("predictions.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 10")
    rows = cur.fetchall()
    con.close()
    
df = pd.DataFrame(rows)
st.write(df)
