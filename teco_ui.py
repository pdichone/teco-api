import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
import time
import json
import math

# Page configuration
st.set_page_config(
    page_title="TECO Energy Outages Map",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
.metric-container {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
.outage-status {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.8rem;
    font-weight: bold;
}
.status-investigating { background-color: #ffd43b; color: #000; }
.status-working { background-color: #fd7e14; color: #fff; }
.status-aware { background-color: #dc3545; color: #fff; }
</style>
""",
    unsafe_allow_html=True,
)


def get_outage_data(api_url: str) -> dict:
    """Fetch outage data from the FastAPI server"""
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error fetching data: {e}")
        return None


def get_marker_color(customers_affected: int) -> str:
    """Return marker color based on number of customers affected"""
    if customers_affected >= 100:
        return "red"
    elif customers_affected >= 10:
        return "orange"
    elif customers_affected >= 5:
        return "yellow"
    else:
        return "green"


def get_polygon_color(customers_affected: int) -> str:
    """Return polygon color based on number of customers affected"""
    if customers_affected >= 100:
        return "#dc3545"  # Red
    elif customers_affected >= 10:
        return "#fd7e14"  # Orange
    elif customers_affected >= 5:
        return "#ffc107"  # Yellow
    else:
        return "#28a745"  # Green


def get_status_class(status: str) -> str:
    """Return CSS class for status styling"""
    if "investigating" in status.lower() or "investigate" in status.lower():
        return "status-investigating"
    elif "working" in status.lower() or "onsite" in status.lower():
        return "status-working"
    elif "aware" in status.lower():
        return "status-aware"
    else:
        return ""


def create_estimated_polygon(
    center_lat: float, center_lon: float, customers_affected: int
) -> list:
    """
    Create an estimated hexagonal polygon around an outage center point
    based on the number of customers affected
    """
    # Estimate radius based on customer count (rough approximation)
    if customers_affected >= 100:
        radius_km = 2.0  # 2km radius for large outages
    elif customers_affected >= 50:
        radius_km = 1.5  # 1.5km radius
    elif customers_affected >= 10:
        radius_km = 1.0  # 1km radius
    else:
        radius_km = 0.5  # 0.5km radius for small outages

    # Convert km to degrees (rough approximation)
    # 1 degree latitude ≈ 111 km
    # 1 degree longitude ≈ 111 km * cos(latitude)
    lat_offset = radius_km / 111.0
    lon_offset = radius_km / (111.0 * math.cos(math.radians(center_lat)))

    # Create a hexagonal polygon (6 sides) around the center point
    polygon_points = []
    for i in range(6):
        angle = (i * 60) * math.pi / 180  # 60 degrees between points
        lat = center_lat + lat_offset * math.sin(angle)
        lon = center_lon + lon_offset * math.cos(angle)
        polygon_points.append([lat, lon])

    return polygon_points


def parse_polygon_from_raw_data(raw_geo_data: dict) -> list:
    """
    Parse polygon coordinates from the raw_geo_data field
    Returns list of [lat, lon] coordinates or None if no valid polygon found
    """
    if not raw_geo_data:
        return None

    # Look for polygon data in the raw_source
    raw_source = raw_geo_data.get("raw_source", {})

    # TECO-specific polygon field names (based on actual data structure)
    teco_polygon_fields = [
        "polygonPoints",  # Main TECO polygon field
        "polygonPointsGoogle",  # Alternative TECO polygon field
    ]

    # Try TECO-specific fields first
    for field in teco_polygon_fields:
        if field in raw_source:
            polygon_data = raw_source[field]

            if polygon_data and isinstance(polygon_data, list):
                try:
                    polygon_points = []

                    # Handle TECO format: [{"lat": 28.123, "lng": -82.456}, ...]
                    for point in polygon_data:
                        if (
                            isinstance(point, dict)
                            and "lat" in point
                            and "lng" in point
                        ):
                            # Convert to [lat, lon] format for folium
                            polygon_points.append([point["lat"], point["lng"]])
                        elif (
                            isinstance(point, dict)
                            and "lat" in point
                            and "lon" in point
                        ):
                            # Alternative format with 'lon' instead of 'lng'
                            polygon_points.append([point["lat"], point["lon"]])
                        elif isinstance(point, list) and len(point) >= 2:
                            # Fallback: handle as coordinate pair
                            # Determine if coordinates are [lat, lon] or [lon, lat]
                            if -90 <= point[0] <= 90 and -180 <= point[1] <= 180:
                                polygon_points.append([point[0], point[1]])
                            elif -90 <= point[1] <= 90 and -180 <= point[0] <= 180:
                                polygon_points.append([point[1], point[0]])

                    if (
                        len(polygon_points) >= 3
                    ):  # Valid polygon needs at least 3 points
                        print(
                            f"✅ Successfully parsed {len(polygon_points)} polygon points from {field}"
                        )
                        return polygon_points

                except Exception as e:
                    print(f"Error parsing TECO polygon from field {field}: {e}")
                    continue

    # Fallback: check for other common polygon field names
    fallback_polygon_fields = [
        "polygon",
        "polygonCoordinates",
        "geometry",
        "coordinates",
        "shape",
        "boundaries",
        "bounds",
        "area_coordinates",
    ]

    for field in fallback_polygon_fields:
        if field in raw_source:
            polygon_data = raw_source[field]

            if polygon_data and isinstance(polygon_data, (list, dict)):
                try:
                    # Handle different polygon formats
                    if isinstance(polygon_data, list):
                        # Check if it's a list of coordinate pairs
                        if len(polygon_data) > 0:
                            first_item = polygon_data[0]

                            # List of [lat, lon] or [lon, lat] pairs
                            if isinstance(first_item, list) and len(first_item) == 2:
                                # Convert to [lat, lon] format for folium
                                polygon_points = []
                                for point in polygon_data:
                                    # Determine if coordinates are [lat, lon] or [lon, lat]
                                    if (
                                        -90 <= point[0] <= 90
                                        and -180 <= point[1] <= 180
                                    ):
                                        polygon_points.append([point[0], point[1]])
                                    elif (
                                        -90 <= point[1] <= 90
                                        and -180 <= point[0] <= 180
                                    ):
                                        polygon_points.append([point[1], point[0]])

                                if len(polygon_points) >= 3:
                                    return polygon_points

                    elif isinstance(polygon_data, dict):
                        # Handle GeoJSON-like structures
                        if "coordinates" in polygon_data:
                            coords = polygon_data["coordinates"]

                            if isinstance(coords, list) and len(coords) > 0:
                                # Get the outer ring
                                outer_ring = (
                                    coords[0] if isinstance(coords[0], list) else coords
                                )

                                if isinstance(outer_ring, list) and len(outer_ring) > 0:
                                    polygon_points = []
                                    for point in outer_ring:
                                        if isinstance(point, list) and len(point) >= 2:
                                            # GeoJSON format is typically [lon, lat]
                                            # Convert to [lat, lon] for folium
                                            polygon_points.append([point[1], point[0]])

                                    if len(polygon_points) >= 3:
                                        return polygon_points

                        # Check for other coordinate formats in dict
                        for coord_field in ["points", "vertices", "coords"]:
                            if coord_field in polygon_data:
                                points = polygon_data[coord_field]
                                if isinstance(points, list) and len(points) >= 3:
                                    return parse_coordinate_list(points)

                except Exception as e:
                    print(f"Error parsing polygon from field {field}: {e}")
                    continue

    return None


def parse_coordinate_list(points: list) -> list:
    """Helper function to parse a list of coordinate points"""
    polygon_points = []
    for point in points:
        if isinstance(point, list) and len(point) >= 2:
            # Determine coordinate order based on value ranges
            lat, lon = point[0], point[1]
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                polygon_points.append([lat, lon])
            elif -90 <= lon <= 90 and -180 <= lat <= 180:
                polygon_points.append([lon, lat])

    return polygon_points if len(polygon_points) >= 3 else None


def create_outage_map(outages_data: dict, show_polygons: bool = True) -> folium.Map:
    """Create an interactive map with outage markers and polygons from /outages endpoint data"""

    # Get outages list from the response
    outages_list = outages_data.get("outages", [])

    # Calculate center point from all outages
    if outages_list:
        lats = []
        lons = []
        for outage in outages_list:
            location = outage.get("location", {})
            if "lat" in location and "lon" in location:
                lats.append(location["lat"])
                lons.append(location["lon"])

        if lats and lons:
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
        else:
            center_lat, center_lon = 27.95, -82.45  # Default Tampa Bay
    else:
        # Default to Tampa Bay area
        center_lat, center_lon = 27.95, -82.45

    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon], zoom_start=10, tiles="OpenStreetMap"
    )

    # Add tile layer options
    folium.TileLayer("cartodbpositron", name="CartoDB Positron").add_to(m)
    folium.TileLayer("cartodbdark_matter", name="CartoDB Dark").add_to(m)

    if not outages_list:
        return m

    # Track polygon statistics
    polygon_count = 0
    estimated_count = 0

    # Add outage markers and polygons
    for outage in outages_list:
        location = outage.get("location", {})
        if "lat" not in location or "lon" not in location:
            continue

        lat = location["lat"]
        lon = location["lon"]
        customers = outage.get("customers_affected", 0)
        incident_id = outage.get("incident_id", "N/A")

        # Get colors
        marker_color = get_marker_color(customers)
        polygon_color = get_polygon_color(customers)

        # Try to parse actual polygon from raw_geo_data
        polygon_coords = None
        raw_geo_data = outage.get("raw_geo_data", {})

        if show_polygons and raw_geo_data:
            polygon_coords = parse_polygon_from_raw_data(raw_geo_data)

            if polygon_coords:
                # Add actual polygon
                folium.Polygon(
                    locations=polygon_coords,
                    color=polygon_color,
                    weight=2,
                    fillColor=polygon_color,
                    fillOpacity=0.3,
                    popup=f"Affected Area - {incident_id} ({customers} customers)",
                    tooltip=f"Service area boundary: {customers} customers affected",
                ).add_to(m)
                polygon_count += 1

            else:
                # Fallback to estimated polygon
                estimated_polygon = create_estimated_polygon(lat, lon, customers)
                folium.Polygon(
                    locations=estimated_polygon,
                    color=polygon_color,
                    weight=2,
                    fillColor=polygon_color,
                    fillOpacity=0.2,  # Slightly more transparent for estimated
                    popup=f"Estimated Affected Area - {incident_id} ({customers} customers)",
                    tooltip=f"Estimated service area: {customers} customers affected",
                ).add_to(m)
                estimated_count += 1

        # Create popup content
        popup_html = f"""
        <div style='width: 320px'>
            <h4>🔧 Incident {incident_id}</h4>
            <p><strong>👥 Customers Affected:</strong> {customers:,}</p>
            <p><strong>📊 Status:</strong> {outage.get('status', 'Unknown')}</p>
            <p><strong>🔍 Reason:</strong> {outage.get('reason', 'Unknown')}</p>
            <p><strong>🕐 Last Updated:</strong><br>{outage.get('last_updated', 'Unknown')}</p>
            {f"<p><strong>⏰ Est. Restoration:</strong><br>{outage.get('estimated_restoration')}</p>" if outage.get('estimated_restoration') else ""}
            <p><strong>📍 Coordinates:</strong><br>{lat:.4f}, {lon:.4f}</p>
            <p><strong>🗺️ Polygon:</strong> {'✅ Actual boundary' if polygon_coords else '⚠️ Estimated area' if show_polygons else '❌ Disabled'}</p>
        </div>
        """

        # Add center point marker
        folium.CircleMarker(
            location=[lat, lon],
            radius=max(8, min(customers / 5, 25)),  # Size based on customers
            popup=folium.Popup(popup_html, max_width=350),
            color="black",
            weight=2,
            fillColor=marker_color,
            fillOpacity=0.8,
            tooltip=f"Incident {incident_id}: {customers} customers",
        ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Store polygon stats for display
    m.polygon_stats = {
        "actual": polygon_count,
        "estimated": estimated_count,
        "total": polygon_count + estimated_count,
    }

    return m


def main():
    """Main Streamlit application"""

    # Header
    st.title("⚡ TECO Energy Outages Map")
    st.markdown("Real-time power outage visualization for TECO Energy service area")

    # Sidebar configuration
    st.sidebar.header("🔧 Configuration")

    # API URL input - updated default to /outages endpoint
    default_url = "http://localhost:8000/outages"
    api_url = st.sidebar.text_input(
        "FastAPI Server URL",
        value=default_url,
        help="URL to your FastAPI server's /outages endpoint",
    )

    # Polygon display option
    show_polygons = st.sidebar.checkbox(
        "🗺️ Show Service Area Polygons",
        value=True,
        help="Display actual service area boundaries (if available) or estimated areas",
    )

    # Debug mode
    debug_mode = st.sidebar.checkbox(
        "🔍 Debug Mode",
        value=False,
        help="Show detailed analysis of polygon data in raw_geo_data",
    )

    # Auto-refresh settings
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh", value=False)
    refresh_interval = st.sidebar.slider(
        "Refresh interval (seconds)",
        min_value=30,
        max_value=300,
        value=60,
        step=30,
        disabled=not auto_refresh,
    )

    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now", type="primary"):
        st.rerun()

    # Load data
    with st.spinner("🔄 Loading outage data..."):
        outages_data = get_outage_data(api_url)

    if not outages_data:
        st.error("Failed to load outage data. Please check your API server.")
        st.stop()

    # Get outages list and summary
    outages_list = outages_data.get("outages", [])
    summary = outages_data.get("summary", {})

    total_outages = len(outages_list)
    total_customers = summary.get(
        "total_customers_affected",
        sum(outage.get("customers_affected", 0) for outage in outages_list),
    )

    # Analyze polygon data availability
    polygon_data_available = 0
    for outage in outages_list:
        raw_geo_data = outage.get("raw_geo_data", {})
        if parse_polygon_from_raw_data(raw_geo_data):
            polygon_data_available += 1

    # Create metrics columns
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(label="🔧 Total Outages", value=total_outages)

    with col2:
        st.metric(label="👥 Customers Affected", value=f"{total_customers:,}")

    with col3:
        avg_customers = total_customers / total_outages if total_outages > 0 else 0
        st.metric(label="📊 Avg. Customers/Outage", value=f"{avg_customers:.1f}")

    with col4:
        st.metric(
            label="🗺️ Actual Polygons",
            value=f"{polygon_data_available}/{total_outages}",
            help="Number of outages with actual service area polygon data",
        )

    with col5:
        data_timestamp = outages_data.get("timestamp", "Unknown")
        if data_timestamp != "Unknown":
            try:
                dt = datetime.fromisoformat(data_timestamp.replace("Z", "+00:00"))
                st.metric(label="🕐 Data Timestamp", value=dt.strftime("%H:%M:%S"))
            except:
                st.metric(label="🕐 Data Timestamp", value="Unknown")
        else:
            st.metric(label="🕐 Data Timestamp", value="Unknown")

    # Polygon data status
    if polygon_data_available > 0:
        st.success(
            f"✅ Found actual polygon data for {polygon_data_available} outages! "
            f"Remaining {total_outages - polygon_data_available} will use estimated areas."
        )
    elif total_outages > 0:
        st.warning(
            "⚠️ No actual polygon boundary data found in raw_geo_data. "
            "All polygons will be estimated based on customer count."
        )

    # Create two columns for map and details
    col_map, col_details = st.columns([3, 1])

    with col_map:
        st.subheader("🗺️ Interactive Outage Map")

        if total_outages > 0:
            # Create and display map
            outage_map = create_outage_map(outages_data, show_polygons=show_polygons)
            map_data = st_folium(outage_map, width=700, height=500)

            # Show polygon statistics if available
            if hasattr(outage_map, "polygon_stats") and show_polygons:
                stats = outage_map.polygon_stats
                st.info(
                    f"🗺️ Polygons: {stats['actual']} actual boundaries, "
                    f"{stats['estimated']} estimated areas, "
                    f"{stats['total']} total displayed"
                )
            elif show_polygons:
                st.info("💡 Click on map markers to see detailed outage information.")
            else:
                st.info(
                    "💡 Polygon display disabled. Enable in sidebar to see service areas."
                )
        else:
            st.success("🎉 No power outages currently reported!")
            # Show empty map centered on Tampa Bay
            empty_map = folium.Map(location=[27.95, -82.45], zoom_start=10)
            st_folium(empty_map, width=700, height=500)

    with col_details:
        st.subheader("📋 Outage Details")

        if total_outages > 0:
            # Create DataFrame for tabular view
            outage_data = []
            for outage in outages_list:
                # Check for actual polygon data
                has_polygon = bool(
                    parse_polygon_from_raw_data(outage.get("raw_geo_data", {}))
                )

                outage_data.append(
                    {
                        "Incident ID": outage.get("incident_id", "N/A"),
                        "Customers": outage.get("customers_affected", 0),
                        "Status": outage.get("status", "Unknown"),
                        "Polygon": "✅ Actual" if has_polygon else "⚠️ Estimated",
                        "Updated": outage.get("last_updated", "Unknown"),
                    }
                )

            df = pd.DataFrame(outage_data)
            df = df.sort_values("Customers", ascending=False)

            # Display table
            st.dataframe(df, hide_index=True, use_container_width=True, height=400)

            # Status breakdown
            st.subheader("📊 Status Breakdown")
            status_counts = df["Status"].value_counts()
            for status, count in status_counts.items():
                status_class = get_status_class(status)
                st.markdown(
                    f'<div class="outage-status {status_class}">{status}: {count}</div>',
                    unsafe_allow_html=True,
                )

        else:
            st.info("No outages to display")

    # Debug section
    if debug_mode and total_outages > 0:
        st.subheader("🔍 Debug: Raw Geo Data Analysis")

        # Show first outage's raw data
        sample_outage = outages_list[0]
        sample_raw_geo = sample_outage.get("raw_geo_data", {})

        st.write("**Sample raw_geo_data structure:**")
        st.json(sample_raw_geo)

        if sample_raw_geo:
            raw_source = sample_raw_geo.get("raw_source", {})
            st.write("**Available fields in raw_source:**")
            st.write(list(raw_source.keys()) if raw_source else "No raw_source data")

            # Look for potential polygon fields
            polygon_candidates = []
            for field, value in raw_source.items():
                if any(
                    keyword in field.lower()
                    for keyword in [
                        "polygon",
                        "geometry",
                        "coordinates",
                        "bounds",
                        "shape",
                        "area",
                    ]
                ):
                    polygon_candidates.append(
                        {
                            "field": field,
                            "type": type(value).__name__,
                            "value": (
                                str(value)[:300] + "..."
                                if len(str(value)) > 300
                                else str(value)
                            ),
                        }
                    )

            if polygon_candidates:
                st.write("**Potential polygon fields found:**")
                for candidate in polygon_candidates:
                    st.write(f"- **{candidate['field']}** ({candidate['type']})")
                    st.code(candidate["value"])
            else:
                st.write("**No polygon-related fields found**")

        # Test polygon parsing on all outages
        st.write("**Polygon parsing results:**")
        parsing_results = []
        for i, outage in enumerate(outages_list[:5]):  # Test first 5 outages
            raw_geo_data = outage.get("raw_geo_data", {})
            parsed_polygon = parse_polygon_from_raw_data(raw_geo_data)
            parsing_results.append(
                {
                    "Incident": outage.get("incident_id", f"#{i}"),
                    "Has raw_geo_data": bool(raw_geo_data),
                    "Polygon parsed": bool(parsed_polygon),
                    "Points count": len(parsed_polygon) if parsed_polygon else 0,
                }
            )

        st.dataframe(pd.DataFrame(parsing_results))

    # Raw data expander
    with st.expander("🔍 Raw /outages Response Data"):
        st.json(outages_data)

    # Footer information
    st.markdown("---")
    st.markdown(
        f"**Data Source:** TECO Energy /outages endpoint | "
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"**API Endpoint:** {api_url} | "
        f"**Polygon Support:** {'✅ Enabled' if show_polygons else '❌ Disabled'}"
    )

    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
