import streamlit as st
import joblib
import pickle
import numpy as np
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

if st.button("Predict"):
    try:
        # Save the data to the SQLite database
        default_price = "Unknown"
        with sql.connect("prediction.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO predictions (year, mileage, tax, mpg, engineSize, predicted_price) VALUES (?, ?, ?, ?, ?, ?)",
              (year, mileage, tax, mpg, engineSize, predicted_price))
            con.commit()
            st.success("Data successfully saved")
#make a prediction
    to_predict_list = [year, mileage, tax, mpg, engineSize]
    result = ValuePredictor(to_predict_list)

     # Display the prediction result
        st.subheader("Prediction Result")
        st.write(f"Harga yang diprediksi: £ {result}")
        
        # Update the database with the prediction result
        with sql.connect("predictions.db") as con:
            cur = con.cursor()
            cur.execute("UPDATE predicted_price SET predicted_price = ? WHERE year = ? AND mileage = ? AND tax = ? AND mpg = ? AND engineSize = ?",
                        (result, year, mileage, tax, mpg, engineSize))
            con.commit()

    except Exception as e:
        st.error(f"An error occurred: {e}")

# Show recent predictions
st.subheader('Data Mobil Audi')
con = sql.connect("prediction.db")
con.row_factory = sql.Row
cur = con.cursor()
cur.execute("SELECT * FROM audi")
rows = cur.fetchall()
con.close()
    
df = pd.DataFrame(rows)
st.write(df)
