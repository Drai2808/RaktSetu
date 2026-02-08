import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="RaktSetu AI",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE = "http://localhost:8000"

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #D61111 !important;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #DC143C;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #FFA500;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .danger-box {
        background-color: #FF0000;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# Helper functions
def check_api_connection():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE}/", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_inventory_status():
    """Get current inventory status"""
    try:
        response = requests.get(f"{API_BASE}/api/v1/inventory/status")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def predict_demand(blood_type, days_ahead):
    """Predict blood demand"""
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/predict",
            json={"blood_type": blood_type, "days_ahead": days_ahead}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_donor_segments():
    """Get donor segmentation"""
    try:
        response = requests.get(f"{API_BASE}/api/v1/donors/segments")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def activate_emergency(event_type, blood_types, severity):
    """Activate emergency mode"""
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/emergency/activate",
            json={
                "event_type": event_type,
                "blood_types_needed": blood_types,
                "severity": severity
            }
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def create_blood_unit(donor_id, blood_type, location):
    """Create blood unit on blockchain"""
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/blockchain/unit/create",
            json={
                "donor_id": donor_id,
                "blood_type": blood_type,
                "collection_date": datetime.now().strftime("%Y-%m-%d"),
                "location": location
            }
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Sidebar
with st.sidebar:
    st.title("🩸 RaktSetu AI")
    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "🔮 Demand Prediction", "⛓️ Blockchain Tracking",
         "👥 Donor Intelligence", "🚨 Emergency Mode", "🔔 Notifications"]
    )

    st.markdown("---")

    # API Status
    if check_api_connection():
        st.success("✅ API Connected")
    else:
        st.error("❌ API Offline")
        st.warning("Start the API server:\n```bash\npython main.py\n```")

# Main content
st.markdown('<h1 class="main-header">🩸 RaktSetu AI - Intelligent Blood Bank Management</h1>', unsafe_allow_html=True)

# PAGE: Dashboard
if page == "📊 Dashboard":
    st.header("📊 Real-Time Dashboard")

    # Get inventory data
    inventory_data = get_inventory_status()

    if inventory_data:
        # Overall health indicator
        overall_health = inventory_data.get("overall_health", "unknown")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Overall Health", overall_health.upper(),
                     delta="Good" if overall_health == "healthy" else "Alert")

        with col2:
            st.metric("Critical Items", inventory_data.get("critical_count", 0))

        with col3:
            total_inventory = sum([item["current_stock"] for item in inventory_data["inventory_status"]])
            st.metric("Total Units", total_inventory)

        with col4:
            st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"))

        st.markdown("---")

        # Inventory Status Table
        st.subheader("📦 Current Inventory Status")

        inventory_items = inventory_data["inventory_status"]

        # Create DataFrame
        df_inventory = pd.DataFrame(inventory_items)

        # Color code by urgency
        def color_urgency(val):
            if val == "critical":
                return "background-color: #D62E0D"
            elif val == "high":
                return "background-color: #1BE038"
            elif val == "medium":
                return "background-color: #d1ecf1"
            else:
                return "background-color: #FAEA02"

        styled_df = df_inventory[["blood_type", "current_stock", "safety_stock",
                                  "optimal_stock", "urgency_level", "days_until_shortage"]].style.applymap(
            color_urgency, subset=["urgency_level"]
        )

        st.dataframe(styled_df, use_container_width=True)

        # Visualization
        col1, col2 = st.columns(2)

        with col1:
            # Stock levels bar chart
            fig_stock = go.Figure()
            fig_stock.add_trace(go.Bar(
                name="Current Stock",
                x=df_inventory["blood_type"],
                y=df_inventory["current_stock"],
                marker_color="#DC143C"
            ))
            fig_stock.add_trace(go.Bar(
                name="Safety Stock",
                x=df_inventory["blood_type"],
                y=df_inventory["safety_stock"],
                marker_color="#FFD700"
            ))
            fig_stock.update_layout(
                title="Stock Levels by Blood Type",
                xaxis_title="Blood Type",
                yaxis_title="Units",
                barmode="group"
            )
            st.plotly_chart(fig_stock, use_container_width=True)

        with col2:
            # Urgency pie chart
            urgency_counts = df_inventory["urgency_level"].value_counts()
            fig_urgency = px.pie(
                values=urgency_counts.values,
                names=urgency_counts.index,
                title="Inventory by Urgency Level",
                color=urgency_counts.index,
                color_discrete_map={
                    "critical": "#dc3545",
                    "high": "#28a745",
                    "medium": "#17a2b8",
                    "low": "#FAEA02"
                }
            )
            st.plotly_chart(fig_urgency, use_container_width=True)

        # Recommendations
        st.subheader("💡 Recommendations")
        critical_items = [item for item in inventory_items if item["urgency_level"] in ["critical", "high"]]

        if critical_items:
            for item in critical_items:
                if item["urgency_level"] == "critical":
                    st.markdown(f'<div class="danger-box">🚨 {item["recommendation"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="warning-box">⚠️ {item["recommendation"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box">✅ All blood types are at healthy levels!</div>', unsafe_allow_html=True)

    else:
        st.error("Unable to fetch inventory data. Make sure the API is running.")

# PAGE: Demand Prediction
elif page == "🔮 Demand Prediction":
    st.header("🔮 AI-Powered Demand Forecasting")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Prediction Settings")

        blood_type = st.selectbox(
            "Select Blood Type",
            ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]
        )

        days_ahead = st.slider(
            "Days to Predict",
            min_value=1,
            max_value=30,
            value=7
        )

        if st.button("🔮 Predict Demand", type="primary"):
            with st.spinner("Analyzing patterns and generating predictions..."):
                prediction_data = predict_demand(blood_type, days_ahead)

                if prediction_data:
                    st.session_state.prediction_data = prediction_data

    with col2:
        if "prediction_data" in st.session_state:
            pred_data = st.session_state.prediction_data

            st.subheader(f"📈 Predictions for {pred_data['blood_type']}")

            # Confidence score
            st.metric("Model Confidence", f"{pred_data['confidence_score']:.1f}%")

            # Predictions table
            predictions = pred_data["predictions"]
            df_pred = pd.DataFrame(predictions)

            # Line chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_pred["date"],
                y=df_pred["predicted_demand"],
                mode="lines+markers",
                name="Predicted Demand",
                line=dict(color="#DC143C", width=3),
                marker=dict(size=8)
            ))

            # Add confidence interval
            fig.add_trace(go.Scatter(
                x=df_pred["date"],
                y=df_pred["confidence_upper"],
                mode="lines",
                name="Upper Bound",
                line=dict(width=0),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=df_pred["date"],
                y=df_pred["confidence_lower"],
                mode="lines",
                name="Confidence Interval",
                fill="tonexty",
                line=dict(width=0),
                fillcolor="rgba(220, 20, 60, 0.2)"
            ))

            fig.update_layout(
                title="Demand Forecast",
                xaxis_title="Date",
                yaxis_title="Units Needed",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Alerts
            if pred_data.get("alerts"):
                st.subheader("🚨 Alerts")
                for alert in pred_data["alerts"]:
                    st.warning(alert)

            # Predictions table
            st.subheader("📋 Detailed Forecast")
            st.dataframe(df_pred, use_container_width=True)

# PAGE: Blockchain Tracking
elif page == "⛓️ Blockchain Tracking":
    st.header("⛓️ Blockchain Traceability System")

    tab1, tab2 = st.tabs(["🆕 Register New Unit", "🔍 Track Unit"])

    with tab1:
        st.subheader("Register New Blood Unit")

        col1, col2 = st.columns(2)

        with col1:
            donor_id = st.text_input("Donor ID", placeholder="D12345")
            blood_type_bc = st.selectbox(
                "Blood Type",
                ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"],
                key="bc_blood_type"
            )

        with col2:
            location = st.text_input("Collection Location", placeholder="Main Blood Bank")

        if st.button("📝 Register on Blockchain", type="primary"):
            if donor_id and location:
                with st.spinner("Creating blockchain record..."):
                    result = create_blood_unit(donor_id, blood_type_bc, location)

                    if result:
                        st.success(f"✅ Blood unit registered successfully!")
                        st.info(f"**Unit ID:** {result['unit_id']}")
                        st.markdown(f"**Blood Type:** {result['blood_type']}")
                        st.markdown(f"**Timestamp:** {result['timestamp']}")

                        # Store in session
                        st.session_state.last_unit_id = result['unit_id']
                    else:
                        st.error("Failed to register unit. Check API connection.")
            else:
                st.error("Please fill in all fields")

    with tab2:
        st.subheader("Track Blood Unit History")

        # Pre-fill if we just created one
        default_unit = st.session_state.get("last_unit_id", "")

        unit_id = st.text_input("Enter Unit ID", value=default_unit, placeholder="UNIT-ABC123DEF456")

        if st.button("🔍 Track Unit", type="primary"):
            if unit_id:
                try:
                    response = requests.get(f"{API_BASE}/api/v1/blockchain/unit/{unit_id}")

                    if response.status_code == 200:
                        data = response.json()

                        # Verification status
                        verification = data.get("verification", {})

                        if verification.get("verified"):
                            st.success("✅ Unit Verified - Authentic")
                        else:
                            st.error("❌ Verification Failed")

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Records", data.get("total_records", 0))
                        with col2:
                            st.metric("Current Status", verification.get("current_status", "unknown").upper())
                        with col3:
                            st.metric("Blockchain Valid", "✅ Yes" if verification.get("blockchain_valid") else "❌ No")

                        # History timeline
                        st.subheader("📜 Complete History")

                        history = data.get("history", [])

                        if history:
                            for record in history:
                                transaction = record["transaction"]

                                with st.expander(f"{transaction['type']} - {transaction['timestamp'][:10]}"):
                                    st.json(transaction)
                        else:
                            st.info("No history found for this unit")
                    else:
                        st.error("Unit not found in blockchain")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a Unit ID")

# PAGE: Donor Intelligence
elif page == "👥 Donor Intelligence":
    st.header("👥 Donor Intelligence & Analytics")

    tab1, tab2, tab3 = st.tabs(["📊 Segments", "📈 Retention", "🗺️ Geographic"])

    with tab1:
        st.subheader("Donor Segmentation")

        if st.button("📊 Load Segments", type="primary"):
            with st.spinner("Analyzing donor database..."):
                segments_data = get_donor_segments()

                if segments_data:
                    st.session_state.segments_data = segments_data

        if "segments_data" in st.session_state:
            data = st.session_state.segments_data
            summary = data.get("summary", {})

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Champions", summary.get("champions", 0))
            with col2:
                st.metric("Regular Donors", summary.get("regular", 0))
            with col3:
                st.metric("At Risk", summary.get("at_risk", 0))
            with col4:
                st.metric("Lost", summary.get("lost", 0))

            # Visualization
            fig = px.bar(
                x=list(summary.keys()),
                y=list(summary.values()),
                labels={"x": "Segment", "y": "Number of Donors"},
                title="Donor Distribution by Segment",
                color=list(summary.values()),
                color_continuous_scale="Reds"
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Retention Metrics")

        if st.button("📈 Analyze Retention", type="primary"):
            try:
                response = requests.get(f"{API_BASE}/api/v1/donors/retention")
                if response.status_code == 200:
                    retention_data = response.json()
                    st.session_state.retention_data = retention_data
            except:
                st.error("Failed to fetch retention data")

        if "retention_data" in st.session_state:
            metrics = st.session_state.retention_data.get("retention_metrics", {})

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Donors", metrics.get("total_donors", 0))
            with col2:
                st.metric("Active Donors", metrics.get("active_donors", 0))
            with col3:
                st.metric("Retention Rate", f"{metrics.get('retention_rate', 0)}%")

            col4, col5 = st.columns(2)

            with col4:
                st.metric("Avg Donations/Donor", metrics.get("average_donations_per_donor", 0))
            with col5:
                st.metric("Emergency Ready", metrics.get("emergency_ready_donors", 0))

    with tab3:
        st.subheader("Geographic Distribution")

        if st.button("🗺️ Load Heatmap", type="primary"):
            try:
                response = requests.get(f"{API_BASE}/api/v1/donors/geographic-heatmap")
                if response.status_code == 200:
                    geo_data = response.json()
                    st.session_state.geo_data = geo_data
            except:
                st.error("Failed to fetch geographic data")

        if "geo_data" in st.session_state:
            geo = st.session_state.geo_data.get("geographic_distribution", {})

            # Create DataFrame for visualization
            geo_df = pd.DataFrame([
                {
                    "Location": loc,
                    "Total Donors": data["total_donors"],
                    "Eligible Donors": data["eligible_donors"],
                    "Emergency Ready": data["emergency_ready"]
                }
                for loc, data in geo.items()
            ])

            fig = px.bar(
                geo_df,
                x="Location",
                y=["Total Donors", "Eligible Donors", "Emergency Ready"],
                title="Donor Distribution by Location",
                barmode="group"
            )
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(geo_df, use_container_width=True)

# PAGE: Emergency Mode
elif page == "🚨 Emergency Mode":
    st.header("🚨 Emergency Response System")

    st.warning("⚠️ Emergency Mode should only be activated for critical situations")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Activate Emergency Response")

        event_type = st.selectbox(
            "Event Type",
            ["accident", "disaster", "outbreak", "festival"]
        )

        blood_types_needed = st.multiselect(
            "Blood Types Needed",
            ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"],
            default=["O+", "O-"]
        )

        severity = st.select_slider(
            "Severity Level",
            options=["low", "medium", "high"],
            value="high"
        )

        if st.button("🚨 ACTIVATE EMERGENCY MODE", type="primary"):
            if blood_types_needed:
                with st.spinner("Activating emergency response..."):
                    result = activate_emergency(event_type, blood_types_needed, severity)

                    if result:
                        st.success("✅ Emergency Mode Activated!")

                        st.markdown(f"**Event Type:** {result['event_type'].title()}")
                        st.markdown(f"**Severity:** {result['severity'].upper()}")
                        st.markdown(f"**Donors Contacted:** {result['donors_contacted']}")
                        st.markdown(f"**Notifications Sent:** {result['notifications_sent']}")

                        st.info(result['message'])

                        # Show current inventory
                        st.subheader("Current Inventory Status")
                        inventory = result.get("current_inventory", [])

                        df_inv = pd.DataFrame(inventory)
                        if not df_inv.empty:
                            st.dataframe(df_inv[["blood_type", "current_stock", "predicted_demand", "urgency_level"]],
                                       use_container_width=True)
                    else:
                        st.error("Failed to activate emergency mode")
            else:
                st.error("Please select at least one blood type")

    with col2:
        st.subheader("Emergency Status")

        if st.button("🔄 Refresh Status"):
            try:
                response = requests.get(f"{API_BASE}/api/v1/emergency/status")
                if response.status_code == 200:
                    status_data = response.json()
                    st.session_state.emergency_status = status_data
            except:
                st.error("Failed to fetch status")

        if "emergency_status" in st.session_state:
            status = st.session_state.emergency_status

            st.metric("System Status", status.get("status", "UNKNOWN"))
            st.metric("Emergency Ready Donors", status.get("emergency_ready_donors", 0))
            st.metric("Critical Items", len(status.get("critical_inventory", [])))

# PAGE: Notifications
elif page == "🔔 Notifications":
    st.header("🔔 Smart Notification System")

    tab1, tab2 = st.tabs(["📤 Send Notification", "📊 Analytics"])

    with tab1:
        st.subheader("Send Notification")

        notif_type = st.selectbox(
            "Notification Type",
            ["Urgency Alert", "Thank You", "Event Notification"]
        )

        if notif_type == "Urgency Alert":
            col1, col2 = st.columns(2)

            with col1:
                blood_type_notif = st.selectbox(
                    "Blood Type",
                    ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"],
                    key="notif_blood_type"
                )
                units_needed = st.number_input("Units Needed", min_value=1, value=10)

            with col2:
                location_notif = st.text_input("Location", value="City Hospital")
                urgency_level = st.selectbox("Urgency", ["low", "medium", "high", "critical"])

            if st.button("📤 Send Alert", type="primary"):
                try:
                    response = requests.post(
                        f"{API_BASE}/api/v1/notifications/urgency",
                        json={
                            "blood_type": blood_type_notif,
                            "units_needed": units_needed,
                            "location": location_notif,
                            "urgency": urgency_level
                        }
                    )

                    if response.status_code == 200:
                        st.success("✅ Notification sent successfully!")
                        result = response.json()
                        st.json(result.get("notification"))
                except Exception as e:
                    st.error(f"Failed to send notification: {str(e)}")

        elif notif_type == "Thank You":
            donor_name = st.text_input("Donor Name")
            blood_type_ty = st.selectbox("Blood Type", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"], key="ty_blood")

            if st.button("📤 Send Thank You", type="primary"):
                try:
                    response = requests.post(
                        f"{API_BASE}/api/v1/notifications/thank-you",
                        json={
                            "donor_name": donor_name,
                            "blood_type": blood_type_ty,
                            "donation_date": datetime.now().strftime("%Y-%m-%d")
                        }
                    )

                    if response.status_code == 200:
                        st.success("✅ Thank you message sent!")
                except Exception as e:
                    st.error(f"Failed to send: {str(e)}")

    with tab2:
        st.subheader("Notification Analytics")

        if st.button("📊 Load Analytics", type="primary"):
            try:
                response = requests.get(f"{API_BASE}/api/v1/notifications/analytics")
                if response.status_code == 200:
                    analytics = response.json().get("analytics", {})
                    st.session_state.notif_analytics = analytics
            except:
                st.error("Failed to load analytics")

        if "notif_analytics" in st.session_state:
            analytics = st.session_state.notif_analytics

            st.metric("Total Notifications Sent", analytics.get("total_sent", 0))

            # By type
            if "by_type" in analytics:
                st.subheader("By Type")
                df_type = pd.DataFrame(list(analytics["by_type"].items()), columns=["Type", "Count"])
                fig = px.pie(df_type, values="Count", names="Type", title="Notifications by Type")
                st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🩸 RaktSetu AI - Intelligent Blood Bank Management System</p>
        <p>Powered by AI, Blockchain & Data Analytics</p>
    </div>
    """,
    unsafe_allow_html=True
)
