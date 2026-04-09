import streamlit as st
import pandas as pd
import numpy as np
import time

# Optional: for serial (Arduino)


# --- PAGE CONFIG ---
st.set_page_config(page_title="Fire Detection Dashboard", layout="wide")

st.title("🔥 IoT Fire Detection and Classification System")

# --- SIDEBAR ---
st.sidebar.header("System Status")
status_placeholder = st.sidebar.empty()

# --- DATA STORAGE ---
data = pd.DataFrame(columns=["MQ2","MQ7","MQ135","Temp","Status"])

# --- OPTIONAL: SERIAL CONNECTION ---
# Change COM port as needed
# ser = serial.Serial('COM3', 9600)

# --- SIMULATION FUNCTION (for testing) ---
def get_sensor_data():
    # Replace this with serial reading later
    mq2 = np.random.randint(200,800)
    mq7 = np.random.randint(150,700)
    mq135 = np.random.randint(200,800)
    temp = np.random.randint(25,100)

    # Simple rule-based classification (replace with ML later)
    if temp > 70 and mq2 > 500:
        status = "FIRE"
    elif mq2 > 400:
        status = "SMOKE"
    else:
        status = "NORMAL"

    return mq2, mq7, mq135, temp, status

# --- MAIN LOOP ---
placeholder = st.empty()

while True:
    # --- GET DATA ---
    mq2, mq7, mq135, temp, status = get_sensor_data()

    # --- APPEND DATA ---
    new_row = {
        "MQ2": mq2,
        "MQ7": mq7,
        "MQ135": mq135,
        "Temp": temp,
        "Status": status
    }

    data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)

    # Keep last 50 rows only
    data = data.tail(50)

    # --- DISPLAY ---
    with placeholder.container():

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("MQ2", mq2)
        col2.metric("MQ7", mq7)
        col3.metric("MQ135", mq135)
        col4.metric("Temperature (°C)", temp)
        col5.metric("Status", status)

        # --- STATUS COLOR ---
        if status == "FIRE":
            st.error("🔥 FIRE DETECTED!")
            status_placeholder.error("FIRE")
        elif status == "SMOKE":
            st.warning("⚠️ Smoke detected")
            status_placeholder.warning("SMOKE")
        else:
            st.success("✅ Normal condition")
            status_placeholder.success("NORMAL")

        # --- CHARTS ---
        st.subheader("Sensor Trends")

        st.line_chart(data[["MQ2","MQ7","MQ135","Temp"]])

        # --- TABLE ---
        st.subheader("Recent Data")
        st.dataframe(data)

    time.sleep(2)
