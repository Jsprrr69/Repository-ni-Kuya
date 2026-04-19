import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from components.footer import display_footer
from datetime import timedelta, datetime
from services.utils import get_risk_level_style
from services.database import get_recent_readings_for_area
from services.sms import check_for_sms, check_if_sent, send_sms, send_email
import logging

logger = logging.getLogger(__name__)

# =====================================================
# GET AREA FROM STATE OR URL PARAMS
# =====================================================
def get_area_from_state_or_params():
    selected_area = None

    if "selected_area" in st.session_state:
        selected_area = st.session_state.selected_area
    elif "area" in st.query_params:
        selected_area = st.query_params["area"]

    return selected_area


# =====================================================
# MAIN DASHBOARD
# =====================================================
selected_area = get_area_from_state_or_params()

if selected_area:

    # Back button
    if st.button("← Back to Visitor Page", type="secondary"):
        st.switch_page("interfaces/visitor.py")

    # Title
    _, area_col, _ = st.columns([1, 8, 1])
    with area_col:
        st.subheader(f"Showing data for {selected_area}")

    # Containers
    status_container = st.empty()
    data_container = st.empty()
    chart_container = st.empty()

    # =====================================================
    # REAL-TIME UPDATE FUNCTION
    # =====================================================
    @st.fragment(run_every=st.session_state.get("refresh_rate", 1))
    def update_sensor_data():

        df = get_recent_readings_for_area(selected_area)

        if df is not None and not df.empty:

            # Remove area_name column if exists
            if "area_name" in df.columns:
                df = df.drop("area_name", axis=1)

            # Latest reading
            latest = df.iloc[0]
            risk_level = latest["fire_risk"]

            # Style
            style = get_risk_level_style(risk_level)

            # ================= STATUS DISPLAY =================
            with status_container:
                st.markdown(
                    f"""
                    <div style="background-color:{style['color']};
                                padding:10px; border-radius:5px; margin-bottom:10px;">
                        <h3 style="color:white; text-align:center;">
                            {style['icon']} Current Status: {risk_level} {style['icon']}
                        </h3>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # ================= TABLE DISPLAY =================
            with data_container:
                display_df = df.copy()

                column_mapping = {
                    "timestamp": "Timestamp",
                    "temperature_reading": "Temperature Level",
                    "air_quality_reading": "Air Quality Level",
                    "carbon_monoxide_reading": "Carbon Monoxide Level",
                    "smoke_reading": "Smoke Level",
                    "fire_risk": "Status"
                }

                display_columns = {
                    k: v for k, v in column_mapping.items()
                    if k in display_df.columns
                }

                display_df = display_df.rename(columns=display_columns)

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )

                # ================= NOTIFICATIONS =================
                with st.expander("Notification Logs"):

                    should_send_sms = check_for_sms(df)

                    if should_send_sms:
                        latest_risk = df.iloc[0]["fire_risk"]

                        already_sent = check_if_sent(selected_area, latest_risk)

                        if not already_sent:
                            sms_result = send_sms(selected_area, latest_risk)

                            if sms_result["sent"]:
                                st.success(f"🚨 {latest_risk} detected! SMS sent.")

                            elif sms_result.get("blocked_by_cooldown"):
                                st.info("⏰ SMS not sent (cooldown active).")

                            else:
                                # Fallback email
                                email_result = send_email(selected_area, latest_risk)

                                if email_result["sent"]:
                                    st.warning("📧 Email sent (SMS failed).")

                                elif email_result.get("blocked_by_cooldown"):
                                    st.info("⏰ Notifications blocked (cooldown).")

                                else:
                                    st.error("❌ SMS and Email both failed.")

                        else:
                            st.info("⏰ Already notified within last hour.")

                    else:
                        st.info("No fire risk pattern detected.")

        else:
            with status_container:
                st.error(f"No data available for {selected_area}")

    # =====================================================
    # SIDEBAR SETTINGS
    # =====================================================
    refresh_rate = st.sidebar.slider(
        "Refresh rate (seconds)",
        min_value=1.0,
        max_value=60.0,
        value=st.session_state.get("refresh_rate", 5.0),
        step=1.0,
        key="refresh_rate"
    )

    # Run updates
    update_sensor_data()

else:
    st.info("No area selected. Please click on an area from the main page.")

# Footer
display_footer()
