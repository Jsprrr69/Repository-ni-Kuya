import streamlit as st
import pandas as pd

from datetime import datetime, timedelta
import random

# =====================================================
# MOCK FUNCTIONS (REPLACEMENTS)
# =====================================================

def get_recent_readings_for_area(area):
    """Generate fake sensor data"""
    now = datetime.now()

    data = []
    for i in range(20):
        data.append({
            "timestamp": now - timedelta(seconds=i * 5),
            "temperature_reading": round(random.uniform(25, 60), 2),
            "air_quality_reading": random.randint(100, 400),
            "carbon_monoxide_reading": random.randint(50, 300),
            "smoke_reading": random.randint(50, 500),
            "fire_risk": random.choice(["LOW", "MEDIUM", "HIGH"])
        })

    return pd.DataFrame(data)


def get_risk_level_style(risk):
    styles = {
        "LOW": {"color": "green", "icon": "✅"},
        "MEDIUM": {"color": "orange", "icon": "⚠️"},
        "HIGH": {"color": "red", "icon": "🚨"}
    }
    return styles.get(risk, styles["LOW"])


def check_for_sms(df):
    return df.iloc[0]["fire_risk"] == "HIGH"


def check_if_sent(area, risk):
    return False  # Always allow for testing


def send_sms(area, risk):
    return {"sent": True}


def send_email(area, risk):
    return {"sent": True}


def display_footer():
    st.markdown("---")
    st.caption("SeekLiyab Fire Detection System Dashboard")


# =====================================================
# GET AREA
# =====================================================
def get_area_from_state_or_params():
    if "selected_area" in st.session_state:
        return st.session_state.selected_area
    return "Area 1"  # Default for testing


# =====================================================
# MAIN DASHBOARD
# =====================================================
selected_area = get_area_from_state_or_params()

st.title("🔥 Fire Detection Dashboard")

# Containers
status_container = st.empty()
data_container = st.empty()
chart_container = st.empty()

# =====================================================
# REAL-TIME UPDATE FUNCTION
# =====================================================
def update_sensor_data():

    df = get_recent_readings_for_area(selected_area)

    if df is not None and not df.empty:

        latest = df.iloc[0]
        risk_level = latest["fire_risk"]
        style = get_risk_level_style(risk_level)

        # ================= STATUS =================
        with status_container:
            st.markdown(
                f"""
                <div style="background-color:{style['color']};
                            padding:10px; border-radius:5px;">
                    <h3 style="color:white; text-align:center;">
                        {style['icon']} Current Status: {risk_level}
                    </h3>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ================= TABLE =================
        with data_container:
            st.dataframe(df, use_container_width=True)

        # ================= CHART =================
        with chart_container:
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df["timestamp"],
                y=df["temperature_reading"],
                name="Temperature"
            ))

            fig.add_trace(go.Scatter(
                x=df["timestamp"],
                y=df["smoke_reading"],
                name="Smoke"
            ))

            st.plotly_chart(fig, use_container_width=True)

        # ================= NOTIFICATIONS =================
        with st.expander("Notification Logs"):
            if check_for_sms(df):
                st.success("🚨 HIGH RISK detected! SMS sent.")
            else:
                st.info("No fire risk detected.")

    else:
        st.error("No data available")


# =====================================================
# REFRESH CONTROL
# =====================================================
refresh_rate = st.sidebar.slider(
    "Refresh rate (seconds)",
    1, 10, 2
)

# Auto refresh loop
import time
while True:
    update_sensor_data()
    time.sleep(refresh_rate)
