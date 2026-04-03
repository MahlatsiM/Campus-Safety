# app.py
import os
import streamlit as st
from datetime import date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from dotenv import load_dotenv

load_dotenv()
from auth.auth_handlers import (
    login_widget,
    logout_widget,
    register_widget,
    reset_password_widget,
    forgot_password_widget,
    forgot_username_widget,
    update_user_details_widget,
    run_query,
    add_user
)

    
# -----------------------------------
# Page setup
# -----------------------------------
st.set_page_config(page_icon="🚨", page_title="Campus Safety Dashboard", layout="wide")
st.title("🚨 Campus Safety Dashboard")

# -----------------------------------
# Configuration
# -----------------------------------
GEOAPIFY_API_KEY = os.environ.get("GEOAPIFY_API_KEY", "")
OPENROUTESERVICE_API_KEY = os.environ.get("OPENROUTESERVICE_API_KEY", "")

# -----------------------------------
# Helper function to decode polyline
# -----------------------------------
def decode_polyline(polyline_str):
    """
    Decode an encoded polyline string into list of (lat, lon) coordinates
    Based on Google's polyline encoding algorithm
    """
    coordinates = []
    index = 0
    lat = 0
    lng = 0
    
    while index < len(polyline_str):
        # Decode latitude
        result = 0
        shift = 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if result & 1 else result >> 1
        lat += dlat
        
        # Decode longitude
        result = 0
        shift = 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if result & 1 else result >> 1
        lng += dlng
        
        coordinates.append((lat / 1e5, lng / 1e5))
    
    return coordinates

# -----------------------------------
# Helper function to get route geometry
# -----------------------------------
@st.cache_data(ttl=3600)
def get_route_geometry(start_lat, start_lon, end_lat, end_lon, debug=False):
    """
    Get actual road path coordinates from OpenRouteService
    Returns list of (lat, lon) tuples representing the route
    """
    try:
        # Use the correct JSON endpoint format
        url = "https://api.openrouteservice.org/v2/directions/foot-walking/json"
        
        # Check if API key is set
        if not OPENROUTESERVICE_API_KEY or OPENROUTESERVICE_API_KEY == "YOUR_OPENROUTESERVICE_API_KEY":
            st.error("🔑 OpenRouteService API key not configured! Please add your API key to the code.")
            return [(start_lat, start_lon), (end_lat, end_lon)]
        
        # OpenRouteService expects the API key without "Bearer" prefix
        headers = {
            'Authorization': OPENROUTESERVICE_API_KEY,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8'
        }
        body = {
            'coordinates': [[start_lon, start_lat], [end_lon, end_lat]]
        }
        
        if debug:
            st.write("**Debug Info:**")
            st.write(f"- URL: {url}")
            st.write(f"- API Key (first 20 chars): {OPENROUTESERVICE_API_KEY[:20]}...")
            st.write(f"- Coordinates: [{start_lon}, {start_lat}] to [{end_lon}, {end_lat}]")
        
        # Increased timeout to 30 seconds
        response = requests.post(url, json=body, headers=headers, timeout=30)
        
        if debug:
            st.write(f"- Response Status: {response.status_code}")
        
        response.raise_for_status()
        
        data = response.json()
        
        # Debug: Show response structure
        if debug:
            st.write(f"- Response type: {type(data)}")
            st.write(f"- Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            st.json(data)
        
        # Check response structure
        if not isinstance(data, dict):
            st.warning(f"⚠️ Unexpected response type: {type(data)}")
            return [(start_lat, start_lon), (end_lat, end_lon)]
        
        if 'routes' not in data:
            st.warning(f"⚠️ No 'routes' key in response. Keys: {list(data.keys())}")
            return [(start_lat, start_lon), (end_lat, end_lon)]
        
        if len(data['routes']) == 0:
            st.warning(f"⚠️ No routes found in response")
            return [(start_lat, start_lon), (end_lat, end_lon)]
        
        # Get the first route
        route = data['routes'][0]
        
        # Check if geometry exists
        if 'geometry' not in route:
            st.warning(f"⚠️ No 'geometry' in route. Route keys: {list(route.keys())}")
            return [(start_lat, start_lon), (end_lat, end_lon)]
        
        geometry = route['geometry']
        
        # Handle different geometry formats (GeoJSON, encoded polyline, etc.)
        if isinstance(geometry, str):
            # Encoded polyline - decode it
            if debug:
                st.write(f"- Decoding polyline: {geometry[:50]}...")
            coords = decode_polyline(geometry)
            # Coordinates are already in (lat, lon) format from decoder
            return coords
        elif isinstance(geometry, dict) and 'coordinates' in geometry:
            # GeoJSON format
            coords = geometry['coordinates']
            # Convert from [lon, lat] to [lat, lon]
            return [(lat, lon) for lon, lat in coords]
        elif isinstance(geometry, list):
            # Already a list of coordinates - assume [lon, lat] format
            return [(lat, lon) for lon, lat in geometry]
        else:
            st.warning(f"⚠️ Unknown geometry format: {type(geometry)}")
            return [(start_lat, start_lon), (end_lat, end_lon)]
        
    except requests.exceptions.Timeout:
        st.warning(f"⏱️ Route calculation timed out after 30 seconds. Check your internet connection or try again later.")
        return [(start_lat, start_lon), (end_lat, end_lon)]
    except requests.exceptions.HTTPError as e:
        # More detailed error for HTTP errors
        error_msg = f"⚠️ HTTP Error ({e.response.status_code}): {e.response.reason}"
        try:
            error_detail = e.response.json()
            if 'error' in error_detail:
                error_msg += f"\n\nAPI Response: {error_detail['error']}"
        except:
            try:
                error_msg += f"\n\nResponse: {e.response.text[:200]}"
            except:
                pass
        
        st.warning(error_msg)
        
        # Additional help for 403 errors
        if e.response.status_code == 403:
            st.error("""
            **🔑 API Key Issue Detected!**
            
            Common causes for 403 Forbidden:
            1. ❌ Invalid API key format
            2. ❌ API key not confirmed via email
            3. ❌ API key doesn't have Directions API enabled
            4. ❌ Rate limit exceeded
            
            **How to fix:**
            1. Go to https://openrouteservice.org/dev/#/home
            2. Log in to your account
            3. Go to "Dashboard" → "Tokens" or "API Keys"
            4. Make sure your token is active and confirmed
            5. Copy the FULL token (the JWT token with dots and equals sign)
            6. Replace it in the code: `OPENROUTESERVICE_API_KEY = "put_token_here"`
            
            The token should look like: eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjFmZTE2...
            """)
        
        return [(start_lat, start_lon), (end_lat, end_lon)]
    except requests.exceptions.RequestException as e:
        st.warning(f"⚠️ Network error: {str(e)}")
        return [(start_lat, start_lon), (end_lat, end_lon)]
    except (KeyError, IndexError, TypeError) as e:
        st.warning(f"❌ Error parsing response: {type(e).__name__} - {str(e)}")
        st.info("💡 Enable debug mode to see the full API response structure")
        return [(start_lat, start_lon), (end_lat, end_lon)]
    except Exception as e:
        st.warning(f"❌ Unexpected error: {type(e).__name__} - {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return [(start_lat, start_lon), (end_lat, end_lon)]

# -----------------------------
# Sidebar Authentication
# -----------------------------
st.sidebar.header("🔐 User Authentication")

# Handle different authentication views
if st.session_state.get("show_register"):
    # Show registration form
    with st.sidebar:
        register_widget()
elif st.session_state.get("show_forgot_password"):
    # Show forgot password form
    with st.sidebar:
        forgot_password_widget()
elif not st.session_state.get("authentication_status"):
    # Show login form
    with st.sidebar:
        login_widget()
else:
    # User is authenticated - show welcome message
    with st.sidebar:
        st.success(f"✅ Logged in as: **{st.session_state.get('name')}**")
        logout_widget()

# Only show account settings if authenticated
if st.session_state.get("authentication_status"):
    with st.sidebar.expander("⚙️ Account Settings"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 Reset Password", use_container_width=True):
                st.session_state["show_reset_password"] = True
        with col2:
            if st.button("✏️ Update Details", use_container_width=True):
                st.session_state["show_update_details"] = True
        
        if st.button("❓ Forgot Username", use_container_width=True):
            st.session_state["show_forgot_username"] = True
    
    # Show modals for settings
    if st.session_state.get("show_reset_password"):
        with st.sidebar:
            reset_password_widget()
            if st.button("❌ Close", use_container_width=True):
                st.session_state["show_reset_password"] = False
                st.rerun()
    
    if st.session_state.get("show_update_details"):
        with st.sidebar:
            update_user_details_widget()
            if st.button("❌ Close", use_container_width=True):
                st.session_state["show_update_details"] = False
                st.rerun()
    
    if st.session_state.get("show_forgot_username"):
        with st.sidebar:
            forgot_username_widget()
            if st.button("❌ Close", use_container_width=True):
                st.session_state["show_forgot_username"] = False
                st.rerun()

# -----------------------------------
# Only show dashboard if authenticated
# -----------------------------------
if st.session_state.get("authentication_status"):
    st.markdown(f"### Welcome back, {st.session_state.get('name')}! 👋")
    
    # -----------------------------------
    # Fetch data for maps
    # -----------------------------------
    try:
        reports_df = pd.DataFrame(run_query("""
            SELECT report_id, user_id, report_type, description, latitude, longitude, created_at
            FROM safety_reports
            ORDER BY created_at DESC
        """), columns=["ID", "User", "Type", "Description", "Lat", "Lon", "Created At"])
    except:
        reports_df = pd.DataFrame(columns=["ID", "User", "Type", "Description", "Lat", "Lon", "Created At"])

    try:
        routes_df = pd.DataFrame(run_query("""
            SELECT route_id, start_lat, start_lon, end_lat, end_lon
            FROM routes
        """), columns=["Route ID", "Start Lat", "Start Lon", "End Lat", "End Lon"])
    except:
        routes_df = pd.DataFrame(columns=["Route ID", "Start Lat", "Start Lon", "End Lat", "End Lon"])

    try:
        safe_areas_df = pd.DataFrame(run_query("""
            SELECT id, name, lat, lon, radius_meters, type
            FROM green_areas
        """), columns=["ID", "Name", "Lat", "Lon", "Radius", "Type"])
    except:
        safe_areas_df = pd.DataFrame(columns=["ID", "Name", "Lat", "Lon", "Radius", "Type"])

    # -----------------------------------
    # Introduction
    # -----------------------------------
    with st.expander("ℹ️ About This Platform", expanded=True):
        st.markdown(
        """
        This Campus Safety and Reporting Platform is designed to give students a secure and accessible way to:
        
        - 🚨 **Report Safety Incidents** - Log safety concerns in real-time with precise location data
        - 🗺️ **View Safety Maps** - Visualize reported incidents, safe routes, and secure areas
        - 📊 **Track Trends** - Monitor safety statistics and patterns across campus
        - 🛡️ **Stay Informed** - Access up-to-date safety information and resources
        
        By promoting a culture of safety, accountability, and awareness, we empower students to take an active 
        role in creating a safer learning environment. Your voice matters, and every report helps make our campus 
        more secure for everyone.
        """)
    
    st.divider()
    
    # -----------------------------------
    # Quick Stats Dashboard
    # -----------------------------------
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_reports = len(reports_df)
        st.metric("📋 Total Reports", total_reports)
    
    with col2:
        user_reports = len(reports_df[reports_df["User"] == st.session_state.get("user_id")]) if not reports_df.empty else 0
        st.metric("📝 Your Reports", user_reports)
    
    with col3:
        safe_zones = len(safe_areas_df)
        st.metric("🟢 Safe Areas", safe_zones)
    
    with col4:
        total_routes = len(routes_df)
        st.metric("🛣️ Safe Routes", total_routes)
    
    st.divider()
    
    # -----------------------------------
    # Map selection
    # -----------------------------------
    st.subheader("🗺️ Interactive Campus Maps")
    
    map_options = ["Safety Reports", "Safe Routes", "Safe Areas"]
    
    # Map selector with custom styling
    selected_map = st.selectbox(
        "Select Map Type",
        map_options,
        help="Choose which map you want to view"
    )

    # Display selected map
    if selected_map == "Safety Reports":
        if not reports_df.empty:
            st.info(f"Showing {len(reports_df)} safety reports on campus")
            
            # Add filter options
            with st.expander("🔍 Filter Reports"):
                    report_types = ["All"] + list(reports_df["Type"].unique())
                    selected_type = st.selectbox("Report Type", report_types)
            
            # Apply filters
            filtered_df = reports_df.copy()
            if selected_type != "All":
                filtered_df = filtered_df[filtered_df["Type"] == selected_type]
            
            # Create map
            fig = px.scatter_mapbox(
                filtered_df, 
                lat="Lat", 
                lon="Lon", 
                color="Type",
                hover_name="Description",
                hover_data={"Lat": False, "Lon": False, "Created At": True, "User": False},
                zoom=13.5, 
                height=600,
                color_discrete_sequence=px.colors.qualitative.Set2,
                size_max=20  # Controls maximum marker size
            )
            # Update marker size
            fig.update_traces(marker=dict(size=9))  # Set marker size (default is ~6)
            
            fig.update_layout(
                mapbox_style="open-street-map", 
                mapbox_center={"lat": -28.743554, "lon": 24.762580},
                margin={"r": 0, "t": 0, "l": 0, "b": 0}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📭 No safety reports to display yet. Be the first to report!")


    elif selected_map == "Safe Routes":
        if not routes_df.empty:
            st.info(f"Showing {len(routes_df)} safe routes on campus")
            
            # Show loading message while fetching routes
            with st.spinner("🗺️ Calculating routes along roads..."):
                # Create base map
                fig = go.Figure()
                
                # Color palette for different routes
                colors = px.colors.qualitative.Set2
                
                # Process each route
                for idx, row in routes_df.iterrows():
                    route_id = row["Route ID"]
                    start_lat = row["Start Lat"]
                    start_lon = row["Start Lon"]
                    end_lat = row["End Lat"]
                    end_lon = row["End Lon"]
                    
                    # Get route geometry from OpenRouteService
                    route_coords = get_route_geometry(start_lat, start_lon, end_lat, end_lon, debug=False)
                    
                    # Extract lats and lons
                    lats = [coord[0] for coord in route_coords]
                    lons = [coord[1] for coord in route_coords]
                    
                    # Add route line
                    color = "green"
                    fig.add_trace(go.Scattermapbox(
                        lat=lats,
                        lon=lons,
                        mode='lines',
                        line=dict(width=4, color=color),
                        name=f"Route {route_id}",
                        hovertemplate=f"<b>Route {route_id}</b><br>" +
                                    "Lat: %{lat:.6f}<br>" +
                                    "Lon: %{lon:.6f}<br>" +
                                    "<extra></extra>"
                    ))
                    
                    # # Add start marker
                    # fig.add_trace(go.Scattermapbox(
                    #     lat=[start_lat],
                    #     lon=[start_lon],
                    #     mode='markers',
                    #     marker=dict(size=12, color='green', symbol='circle'),
                    #     name=f"Start {route_id}",
                    #     hovertemplate=f"<b>Route {route_id} - Start</b><br>" +
                    #                 f"Lat: {start_lat:.6f}<br>" +
                    #                 f"Lon: {start_lon:.6f}<br>" +
                    #                 "<extra></extra>",
                    #     showlegend=False
                    # ))
                    
                    # # Add end marker
                    # fig.add_trace(go.Scattermapbox(
                    #     lat=[end_lat],
                    #     lon=[end_lon],
                    #     mode='markers',
                    #     marker=dict(size=12, color='green', symbol='circle'),
                    #     name=f"End {route_id}",
                    #     hovertemplate=f"<b>Route {route_id} - End</b><br>" +
                    #                 f"Lat: {end_lat:.6f}<br>" +
                    #                 f"Lon: {end_lon:.6f}<br>" +
                    #                 "<extra></extra>",
                    #     showlegend=False
                    # ))
                
                # Update layout
                fig.update_layout(
                    mapbox=dict(
                        style="open-street-map",
                        center=dict(lat=-28.743554, lon=24.762580),
                        zoom=15
                    ),
                    height=600,
                    margin={"r": 0, "t": 0, "l": 0, "b": 0},
                    showlegend=True,
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01,
                        bgcolor="rgba(255, 255, 255, 0.8)"
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            # Show route information
            with st.expander("📊 Route Details"):
                st.dataframe(
                    routes_df[["Route ID", "Start Lat", "Start Lon", "End Lat", "End Lon"]],
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("🛣️ No safe routes available yet.")

    elif selected_map == "Safe Areas":
        if not safe_areas_df.empty:
            st.info(f"Showing {len(safe_areas_df)} safe areas on campus")
            
            fig = px.scatter_mapbox(
                safe_areas_df,
                lat="Lat",
                lon="Lon",
                size="Radius",
                color="Type",
                hover_name="Name",
                size_max=80,
                zoom=14.5,
                height=600,
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig.update_layout(
                mapbox_style="open-street-map", 
                mapbox_center={"lat": -28.750216, "lon": 24.759346},
                margin={"r": 0, "t": 0, "l": 0, "b": 0}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🟢 No safe areas available yet.")

    st.divider()

    # -----------------------------------
    # Report distributions
    # -----------------------------------
    st.subheader("📊 Safety Analytics")
    
    if not reports_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Reports by type
            type_counts = reports_df["Type"].value_counts().reset_index()
            type_counts.columns = ["Type", "Count"]
            fig1 = px.bar(
                type_counts, 
                x="Type", 
                y="Count", 
                title="Reports by Type", 
                color="Type",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig1.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Reports by type (pie chart)
            fig2 = px.pie(
                type_counts, 
                values="Count", 
                names="Type", 
                title="Report Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Recent reports table
        st.subheader("📋 Recent Reports")
        display_df = reports_df.head(10)[["Type", "Description", "Created At"]].copy()
        display_df["Created At"] = pd.to_datetime(display_df["Created At"]).dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("📊 No data available for analytics yet. Submit a report to get started!")

    st.divider()

    # -----------------------------------
    # Report Submission Form
    # -----------------------------------
    st.subheader("📝 Submit a New Safety Report")

    user_id = st.session_state.get("user_id")

    # Check daily limit
    try:
        result = run_query(
            """
            SELECT COUNT(*) 
            FROM safety_reports
            WHERE user_id = %s AND DATE(created_at) = %s
            """,
            (user_id, date.today())
        )
        today_count = result[0][0] if result else 0
        st.info(f"📊 Reports submitted today: **{today_count}/3**")

        if today_count >= 3:
            st.warning("⚠️ You have reached the maximum of 3 reports for today. Please try again tomorrow.")
        else:
            with st.form("location_form"):
                st.markdown("**Step 1: Search & Confirm Location**")
                location_input = st.text_input(
                    "📍 Enter location name",
                    placeholder="Start typing a location...",
                    help="Type a location name to see suggestions"
                )

                latitude = None
                longitude = None
                selected_location = None
                location_confirmed = False

                if location_input:
                    try:
                        url = f"https://api.geoapify.com/v1/geocode/autocomplete?text={location_input}&limit=5&apiKey={GEOAPIFY_API_KEY}"
                        response = requests.get(url, timeout=5)
                        response.raise_for_status()
                        data = response.json()
                        results = data.get("features", [])

                        if results:
                            options = [r['properties']['formatted'] for r in results]
                            selected_location = st.selectbox("📌 Select a location", options)

                            for r in results:
                                if r['properties']['formatted'] == selected_location:
                                    latitude = r['properties']['lat']
                                    longitude = r['properties']['lon']
                                    st.caption(f"Coordinates: {latitude:.6f}, {longitude:.6f}")
                                    break
                        else:
                            st.info("🔍 No suggestions found. Try a different search term.")
                    except requests.exceptions.Timeout:
                        st.error("⏱️ Location search timed out. Please try again.")
                    except Exception as e:
                        st.error(f"❌ Error fetching location: {str(e)}")

                confirm_btn = st.form_submit_button("✅ Confirm Location")
                if confirm_btn and selected_location:
                    location_confirmed = True
                    st.session_state['latitude'] = latitude
                    st.session_state['longitude'] = longitude
                    st.session_state['selected_location'] = selected_location
                    st.success(f"Location confirmed: {selected_location}")

            # -----------------------------------
            # Step 2: Submit report form (enabled only if location confirmed)
            # -----------------------------------
            if location_confirmed or ('latitude' in st.session_state and 'longitude' in st.session_state):
                with st.form("report_form", clear_on_submit=True):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        report_type = st.selectbox(
                            "Report Type",
                            ["Hazard", "Theft", "Suspicious Activity", "Assault", "Vandalism", "Other"],
                            help="Select the type of incident you want to report"
                        )
                        description = st.text_area(
                            "Description",
                            placeholder="Please provide details about the incident...",
                            height=150,
                            help="Be as specific as possible"
                        )
                    with col2:
                        st.markdown("**Location Information**")
                        st.caption(f"Confirmed location: {st.session_state['selected_location']}")
                        st.caption(f"Coordinates: {st.session_state['latitude']:.6f}, {st.session_state['longitude']:.6f}")

                    submit_btn = st.form_submit_button("🚨 Submit Report", use_container_width=True)

                if submit_btn:
                    if not user_id:
                        st.error("❌ User ID not found. Please log in again.")
                    elif not (report_type and description):
                        st.error("⚠️ Please fill in all fields before submitting.")
                    else:
                        try:
                            run_query(
                                """
                                INSERT INTO safety_reports (user_id, report_type, description, latitude, longitude, created_at)
                                VALUES (%s, %s, %s, %s, %s, NOW())
                                """,
                                (
                                    user_id,
                                    report_type,
                                    description,
                                    st.session_state['latitude'],
                                    st.session_state['longitude']
                                ),
                                fetch=False
                            )
                            st.success("✅ Report submitted successfully! Thank you for keeping our campus safe.")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to submit report: {e}")

    except Exception as e:
        st.error(f"Error checking report limit: {e}")


else:
    # Not authenticated - show welcome screen
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## Welcome to the Campus Safety Dashboard 🎓
        
        Your trusted platform for campus safety and incident reporting.
        
        ### 🌟 Features
        
        - **🚨 Real-Time Reporting** - Report safety incidents instantly with precise location tracking
        - **🗺️ Interactive Maps** - View safety reports, safe routes, and secure areas on campus
        - **📊 Analytics Dashboard** - Track safety trends and statistics
        - **🔒 Secure & Anonymous** - Your privacy is our priority
        - **👥 Community-Driven** - Help create a safer campus for everyone
        
        ### 🎯 Our Mission
        
        We're committed to fostering a culture of safety, accountability, and awareness by empowering 
        students to take an active role in campus security. Every report helps make our community safer.
        
        ### 🚀 Get Started
        
        **👈 Please log in or create an account** using the sidebar to access all features.
        """)
    
    with col2:
        st.info("""
        ### 📱 Quick Stats
        
        Join our growing community of safety-conscious students!
        """)
        
        # Show some public statistics
        try:
            total_reports = run_query("SELECT COUNT(*) FROM safety_reports")
            total_users = run_query("SELECT COUNT(*) FROM users")
            
            if total_reports:
                st.metric("Total Reports", total_reports[0][0])
            if total_users:
                st.metric("Active Users", total_users[0][0])
        except:
            pass
        
        st.success("✨ Free to use\n\n🔐 Secure & private\n\n⚡ Fast reporting")
    
    st.markdown("---")
    
    # Emergency contacts
    with st.expander("🆘 Emergency Contacts", expanded=False):
        st.markdown("""
        ### Campus Security
        - **Control Room**: 📞 053 491 0911
        - **Client Service Centre**: 📞 053 491 0365
        
        ### Other Emergency Services
        - **Police (SAPS)**: 📞 10111
        - **Crime Stop (Anonymous Reporting)**: 📞 08600 10111
        - **Ambulance (ER24)**: 📞 084 124
        - **Ambulance (Public)**: 📞 10177 / 053 802 9111
        - **Fire Brigade**: 📞 053 832 4211
        """)
    
    # Tips for staying safe
    with st.expander("💡 Safety Tips", expanded=False):
        st.markdown("""
        ### Stay Safe on Campus
        
        1. **🌙 Travel in Groups** - Especially at night
        2. **📱 Keep Your Phone Charged** - Always stay connected
        3. **🚶 Use Well-Lit Paths** - Stick to main walkways
        4. **👀 Stay Alert** - Be aware of your surroundings
        5. **🔐 Lock Your Belongings** - Don't leave valuables unattended
        6. **📞 Save Emergency Numbers** - Quick access is crucial
        7. **🗣️ Report Suspicious Activity** - Help keep everyone safe
        """)

st.caption("🚨 Campus Safety Dashboard | This platform refreshes every 10 minutes")