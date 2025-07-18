<!-- @format -->

# TECO Energy Outage API & Visualization Suite

🔌 **Real-time Power Outage Data for TECO Energy Service Area**

A complete solution for accessing, processing, and visualizing TECO Energy's power outage data with FastAPI backend, Streamlit frontend, and comprehensive GIS support.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Running the Applications](#running-the-applications)
- [API Documentation](#api-documentation)
- [Frontend Applications](#frontend-applications)
- [Response Formats](#response-formats)
- [GIS Data Support](#gis-data-support)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 🎯 Overview

This project provides a complete solution for accessing TECO Energy's real-time power outage data through:

- **FastAPI Backend**: RESTful API server with caching, authentication, and multiple data formats
- **Streamlit Web App**: Interactive map visualization with actual service area polygons
- **Core API Client**: Direct access to TECO's Elasticsearch backend
- **GIS Support**: Full geographic data preservation with polygon boundaries

### Data Source

- **TECO Energy Outage Map**: https://outage.tecoenergy.com/
- **Backend**: Elasticsearch-based geospatial data with actual service area polygons
- **Coverage**: Tampa Bay area and TECO service territory in Florida
- **Update Frequency**: Real-time (typically every 5-10 minutes)

---

## ✨ Features

### 🚀 FastAPI Backend (`teco_fastapi.py`)

- ✅ **Real-time outage data** from TECO Energy
- ✅ **Automatic session management** - no manual API keys needed
- ✅ **Geographic filtering** by latitude/longitude bounding box
- ✅ **Smart caching** (5-minute TTL) to prevent API abuse
- ✅ **Multiple output formats**: Standard JSON, GeoJSON, Raw Elasticsearch
- ✅ **CORS support** for web applications
- ✅ **Interactive API documentation** with Swagger UI

### 🗺️ Streamlit Web App (`teco_ui.py`)

- 🗺️ **Interactive maps** with Leaflet/Folium integration
- 🗺️ **Real service area polygons** from TECO's actual boundary data
- 🗺️ **Clickable markers and polygons** with detailed popup information
- 🗺️ **Live statistics** and outage summaries
- 🗺️ **Debug mode** for data structure analysis
- 🗺️ **Auto-refresh** capabilities
- 🗺️ **Multiple map tile layers** (OpenStreetMap, CartoDB, etc.)

### 🔧 Core API Client (`teco_uni_api.py`)

- ⚡ **Direct Elasticsearch access** to TECO's backend
- ⚡ **Automatic authentication** with session key extraction
- ⚡ **Request retry logic** with exponential backoff
- ⚡ **Rate limiting** to be respectful to TECO's servers
- ⚡ **Comprehensive error handling** and logging
- ⚡ **Polygon data extraction** with complete coordinate preservation

### 🗺️ GIS & Mapping Support

- 🗺️ **Complete polygon/geometry data** preservation from TECO
- 🗺️ **GeoJSON output** for mapping libraries (Leaflet, Mapbox, etc.)
- 🗺️ **Actual service area boundaries** (not estimated circles)
- 🗺️ **Coordinate precision** maintained from source
- 🗺️ **WGS84 (EPSG:4326)** coordinate system support

---

## 📁 Project Structure

```
teco-outage-api/
├── teco_fastapi.py          # FastAPI server with REST endpoints
├── teco_uni_api.py          # Core TECO API client
├── teco_ui.py               # Streamlit web application
├── requirements.txt         # Python dependencies
├── README.md               # This documentation
└── __pycache__/            # Python cache (auto-generated)
```

### File Descriptions

- **`teco_fastapi.py`**: FastAPI server that provides RESTful endpoints for outage data
- **`teco_uni_api.py`**: Core client library that interfaces directly with TECO's Elasticsearch API
- **`teco_ui.py`**: Streamlit web application with interactive maps and visualizations
- **`requirements.txt`**: All required Python packages for the project

---

## 🏃 Quick Start

### 1. Prerequisites

- **Python 3.8+**
- **Internet connection** (to access TECO's API)
- **Modern web browser** (for Streamlit interface)

### 2. Clone/Download Project

```bash
# Download all files to a directory
mkdir teco-outage-api
cd teco-outage-api

# Ensure you have these files:
# - teco_fastapi.py
# - teco_uni_api.py
# - teco_ui.py
# - requirements.txt
```

### 3. Install Dependencies

#### Option A: Using uv (Recommended)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies
uv add fastapi uvicorn streamlit folium streamlit-folium pandas requests python-multipart
```

#### Option B: Using pip

```bash
# Install dependencies
pip install fastapi uvicorn streamlit folium streamlit-folium pandas requests python-multipart
```

### 4. Start the Applications

#### Terminal 1: Start FastAPI Backend

```bash
# Using uv
uv run uvicorn teco_fastapi:app --host 0.0.0.0 --port 8000 --reload

# Using uvicorn directly
uvicorn teco_fastapi:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2: Start Streamlit Frontend

```bash
# Using uv
uv run streamlit run teco_ui.py

# Using streamlit directly
streamlit run teco_ui.py
```

### 5. Access the Applications

- **Streamlit Web App**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Root**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health

---

## 🔧 Installation

### Prerequisites

```bash
# Check Python version (3.8+ required)
python --version

# Ensure pip is available
pip --version
```

### Method 1: Using uv (Recommended)

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to project directory
cd teco-outage-api

# Install all dependencies at once
uv add fastapi uvicorn streamlit folium streamlit-folium pandas requests python-multipart

# Alternative: Install from requirements.txt
uv pip install -r requirements.txt
```

### Method 2: Using pip

```bash
# Install core dependencies
pip install fastapi uvicorn streamlit folium streamlit-folium pandas requests python-multipart

# Or install from requirements.txt
pip install -r requirements.txt
```

### Method 3: Using conda

```bash
# Create environment
conda create -n teco-api python=3.11
conda activate teco-api

# Install dependencies
pip install fastapi uvicorn streamlit folium streamlit-folium pandas requests python-multipart
```

### Verify Installation

```bash
# Test Python imports
python -c "import fastapi, uvicorn, streamlit, folium, requests; print('✅ All dependencies installed successfully')"
```

---

## 🚀 Running the Applications

### Running Everything Locally

#### Step 1: Start the FastAPI Backend Server

Open your first terminal/command prompt and run:

```bash
# Navigate to project directory
cd teco-outage-api

# Start FastAPI server (choose one method)

# Method 1: Using uv
uv run uvicorn teco_fastapi:app --host 0.0.0.0 --port 8000 --reload

# Method 2: Using uvicorn directly
uvicorn teco_fastapi:app --host 0.0.0.0 --port 8000 --reload

# Method 3: Using Python directly
python -m uvicorn teco_fastapi:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**

```
🚀 Starting TECO Outage API Server...
📖 Documentation will be available at: http://localhost:8000/docs
🔗 API root: http://localhost:8000/
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

#### Step 2: Start the Streamlit Frontend

Open your second terminal/command prompt and run:

```bash
# Navigate to project directory (if not already there)
cd teco-outage-api

# Start Streamlit app (choose one method)

# Method 1: Using uv
uv run streamlit run teco_ui.py

# Method 2: Using streamlit directly
streamlit run teco_ui.py

# Method 3: Custom port
streamlit run teco_ui.py --server.port 8501
```

**Expected Output:**

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501

  Ready to go!
```

#### Step 3: Access the Applications

1. **Streamlit Web Interface**: Open http://localhost:8501 in your browser
2. **API Documentation**: Open http://localhost:8000/docs for interactive API docs
3. **API Health Check**: Visit http://localhost:8000/health to verify backend status

### Command Reference

#### FastAPI Server Commands

```bash
# Development (auto-reload on file changes)
uvicorn teco_fastapi:app --host 0.0.0.0 --port 8000 --reload

# Production (multiple workers)
uvicorn teco_fastapi:app --host 0.0.0.0 --port 8000 --workers 4

# Custom port
uvicorn teco_fastapi:app --host 0.0.0.0 --port 3001 --reload

# With access logs
uvicorn teco_fastapi:app --host 0.0.0.0 --port 8000 --access-log --reload
```

#### Streamlit Commands

```bash
# Basic start
streamlit run teco_ui.py

# Custom port
streamlit run teco_ui.py --server.port 8502

# Custom host (for network access)
streamlit run teco_ui.py --server.address 0.0.0.0

# Disable auto-rerun
streamlit run teco_ui.py --server.fileWatcherType none
```

### Testing Your Setup

#### 1. Test FastAPI Backend

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test outages endpoint
curl http://localhost:8000/outages

# Expected: JSON response with outage data
```

#### 2. Test Streamlit Frontend

1. Open http://localhost:8501
2. You should see the TECO Energy Outages Map interface
3. Click "🧪 Load Test Data" to test functionality
4. Verify map displays with markers and polygons

### Stopping the Applications

```bash
# Stop FastAPI server: Press Ctrl+C in the FastAPI terminal
# Stop Streamlit app: Press Ctrl+C in the Streamlit terminal
```

---

## 📡 API Documentation

### Quick API Reference

#### Core Endpoints

| Endpoint           | Method | Description                             |
| ------------------ | ------ | --------------------------------------- |
| `/`                | GET    | API information and available endpoints |
| `/health`          | GET    | Health check and system status          |
| `/outages`         | GET    | All current outages with complete data  |
| `/outages/summary` | GET    | Summary statistics only                 |
| `/outages/bbox`    | GET    | Outages within geographic bounding box  |
| `/outages/geojson` | GET    | Outages in GeoJSON format for mapping   |
| `/outages/raw`     | GET    | Raw Elasticsearch response from TECO    |

#### Example API Calls

**Get All Outages:**

```bash
curl http://localhost:8000/outages
```

**Get Summary Statistics:**

```bash
curl http://localhost:8000/outages/summary
```

**Get Outages in Tampa Area:**

```bash
curl "http://localhost:8000/outages/bbox?north=28.1&south=27.8&east=-82.3&west=-82.7"
```

**Get GeoJSON for Mapping:**

```bash
curl http://localhost:8000/outages/geojson
```

### Interactive API Documentation

Once your FastAPI server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive documentation where you can test API endpoints directly in your browser.

---

## 🖥️ Frontend Applications

### Streamlit Web Application (`teco_ui.py`)

The Streamlit app provides a complete web interface for visualizing TECO outage data.

#### Features:

- **🗺️ Interactive Maps**: Click markers and polygons for details
- **📊 Live Statistics**: Real-time outage counts and customer impact
- **🎛️ Control Panel**: Configure API endpoint, polygon display, debug mode
- **🔄 Auto-refresh**: Automatic data updates at configurable intervals
- **🧪 Test Data**: Load sample data for testing without real outages

#### Using the Streamlit Interface:

1. **Start the Application**:

   ```bash
   streamlit run teco_ui.py
   ```

2. **Configure Settings** (in left sidebar):

   - **FastAPI Server URL**: Usually `http://localhost:8000/outages`
   - **Show Service Area Polygons**: Toggle actual TECO boundary display
   - **Debug Mode**: View raw data structures
   - **Auto-refresh**: Enable automatic data updates

3. **Load Data**:

   - **🔄 Refresh Data**: Get latest outages from TECO
   - **🧪 Load Test Data**: Use sample data for testing

4. **Interact with Map**:
   - **Click markers**: View detailed outage information
   - **Click polygons**: See service area details
   - **Zoom/pan**: Navigate around Tampa Bay area

#### Map Features:

- **Real Polygons**: Actual TECO service area boundaries (when available)
- **Estimated Areas**: Fallback hexagonal polygons based on customer count
- **Color Coding**: Red (100+ customers), Orange (10-99), Yellow (5-9), Green (1-4)
- **Multiple Tile Layers**: OpenStreetMap, CartoDB Positron, CartoDB Dark

---

## 📊 Response Formats

### Standard API Response

```json
{
  "summary": {
    "total_outages": 7,
    "total_customers_affected": 15,
    "last_updated": "2025-07-18T00:10:34.610929",
    "data_source": "TECO Energy"
  },
  "outages": [
    {
      "incident_id": "A202519903470",
      "location": {
        "lat": 28.38186640739118,
        "lon": -82.18639782509501
      },
      "customers_affected": 1,
      "status": "We're aware of the outage",
      "reason": "Pending Investigation",
      "last_updated": "2025-07-18T03:05:06",
      "estimated_restoration": "2025-07-18T06:00:00",
      "raw_geo_data": {
        "polygon_center": [-82.18639782509501, 28.38186640739118],
        "elasticsearch_id": "dju2v9k4u",
        "raw_source": {
          "incidentId": "A202519903470",
          "polygonPoints": [
            { "lat": 28.381867039307426, "lng": -82.18593136007762 },
            { "lat": 28.38170911946569, "lng": -82.18596659333919 }
            // ... more boundary points
          ],
          "polygonPointsGoogle": [
            // Alternative polygon format
          ]
        }
      }
    }
  ]
}
```

### GeoJSON Format

```json
{
  "type": "FeatureCollection",
  "metadata": {
    "generated": "2025-07-18T00:10:34.610929",
    "count": 7,
    "data_source": "TECO Energy",
    "coordinate_system": "WGS84 (EPSG:4326)"
  },
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-82.18639782509501, 28.38186640739118]
      },
      "properties": {
        "incident_id": "A202519903470",
        "customers_affected": 1,
        "status": "We're aware of the outage",
        "reason": "Pending Investigation"
      }
    }
  ]
}
```

---

## 🗺️ GIS Data Support

### Polygon Data Extraction

This project extracts **actual service area polygons** from TECO's Elasticsearch backend:

- **Source**: TECO's internal GIS system
- **Format**: Array of {"lat": float, "lng": float} objects
- **Precision**: 15-20 coordinate points per polygon
- **Accuracy**: Exact service area boundaries (not estimates)

#### How Polygon Data Flows:

1. **TECO Elasticsearch API** → Returns `polygonPoints` arrays
2. **`teco_uni_api.py`** → Extracts complete polygon data
3. **`teco_fastapi.py`** → Preserves all original data in `raw_source`
4. **`teco_ui.py`** → Parses and renders actual service area boundaries

### Coordinate System

- **Standard**: WGS84 (EPSG:4326)
- **Format**: [longitude, latitude] (GeoJSON standard) for API, [latitude, longitude] for map display
- **Precision**: Full precision maintained from TECO's source

### Integration with GIS Applications

#### Web Mapping Libraries

```javascript
// Leaflet.js example
fetch('http://localhost:8000/outages/geojson')
  .then((response) => response.json())
  .then((data) => {
    L.geoJSON(data).addTo(map);
  });
```

#### Python GIS

```python
# GeoPandas example
import geopandas as gpd
import requests

response = requests.get('http://localhost:8000/outages/geojson')
gdf = gpd.read_file(response.text, driver='GeoJSON')
gdf.plot(column='customers_affected', cmap='Reds')
```

#### Desktop GIS (QGIS)

1. Layer → Add Layer → Add Vector Layer
2. Source Type: Protocol HTTP(S), cloud, etc.
3. URI: `http://localhost:8000/outages/geojson`
4. Format: GeoJSON

---

## ⚙️ Configuration

### Environment Variables (Optional)

```bash
# Set cache duration (default: 300 seconds)
export TECO_API_CACHE_TTL=300

# Set rate limiting delay (default: 1.0 second)
export TECO_API_RATE_LIMIT=1.0

# Set maximum retry attempts (default: 3)
export TECO_API_MAX_RETRIES=3
```

### Server Configuration Options

#### FastAPI Server

```bash
# Development mode (auto-reload)
uvicorn teco_fastapi:app --host 0.0.0.0 --port 8000 --reload

# Production mode (multiple workers)
uvicorn teco_fastapi:app --host 0.0.0.0 --port 8000 --workers 4

# Custom configuration
uvicorn teco_fastapi:app --host 0.0.0.0 --port 8000 --log-level info --access-log
```

#### Streamlit Configuration

```bash
# Custom port
streamlit run teco_ui.py --server.port 8502

# Allow external connections
streamlit run teco_ui.py --server.address 0.0.0.0

# Disable file watching
streamlit run teco_ui.py --server.fileWatcherType none
```

### Application Settings

#### Streamlit App Configuration

In the sidebar, you can configure:

- **API Endpoint**: URL to your FastAPI server
- **Polygon Display**: Show actual vs estimated polygons
- **Debug Mode**: View raw data structures
- **Auto-refresh**: Automatic data updates (30-300 seconds)

#### API Cache Settings

The FastAPI server caches responses for 5 minutes by default. You can:

- Clear cache: `curl -X POST http://localhost:8000/cache/clear`
- Disable cache: Add `?use_cache=false` to API requests
- Check cache status: Visit `http://localhost:8000/stats`

---

## 🚀 Deployment

### Local Network Access

#### Make Services Available on Network

```bash
# FastAPI - accessible from other devices
uvicorn teco_fastapi:app --host 0.0.0.0 --port 8000

# Streamlit - accessible from other devices
streamlit run teco_ui.py --server.address 0.0.0.0
```

Access from other devices using your computer's IP address:

- **FastAPI**: `http://192.168.1.100:8000` (replace with your IP)
- **Streamlit**: `http://192.168.1.100:8501`

### Cloud Deployment Options

#### Railway (Recommended for FastAPI)

1. Create account at [Railway.app](https://railway.app)
2. Upload your project files
3. Railway will auto-detect FastAPI and deploy
4. Get public URL: `https://your-app.railway.app`

#### Streamlit Cloud (For Streamlit App)

1. Create account at [share.streamlit.io](https://share.streamlit.io)
2. Connect GitHub repository
3. Deploy directly from GitHub
4. Configure to point to your deployed FastAPI URL

#### VPS/Cloud Server

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip nginx

# Install project dependencies
pip3 install fastapi uvicorn streamlit folium streamlit-folium pandas requests

# Run FastAPI with systemd/supervisor
uvicorn teco_fastapi:app --host 0.0.0.0 --port 8000

# Run Streamlit
streamlit run teco_ui.py --server.address 0.0.0.0 --server.port 8501
```

### Docker Deployment

#### Dockerfile for FastAPI

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY teco_fastapi.py teco_uni_api.py ./
EXPOSE 8000

CMD ["uvicorn", "teco_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Commands

```bash
# Build FastAPI image
docker build -t teco-api .

# Run FastAPI container
docker run -p 8000:8000 teco-api

# Run Streamlit container (separate)
docker run -p 8501:8501 -e API_URL=http://localhost:8000 teco-streamlit
```

---

## 💡 Examples

### Basic Usage Examples

#### Monitor Outages with Python

```python
import requests
import time

def monitor_outages():
    while True:
        response = requests.get('http://localhost:8000/outages/summary')
        data = response.json()

        print(f"Current outages: {data['total_outages']}")
        print(f"Customers affected: {data['total_customers_affected']}")

        if data['total_customers_affected'] > 1000:
            print("🚨 MAJOR OUTAGE DETECTED!")

        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    monitor_outages()
```

#### Simple Web Dashboard

```html
<!DOCTYPE html>
<html>
  <head>
    <title>TECO Outages</title>
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  </head>
  <body>
    <div id="map" style="height: 400px;"></div>
    <div id="stats"></div>

    <script>
      const map = L.map('map').setView([27.95, -82.45], 10);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(
        map
      );

      async function loadOutages() {
        try {
          const response = await fetch('http://localhost:8000/outages/geojson');
          const data = await response.json();

          L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
              return L.circleMarker(latlng, {
                radius: Math.max(5, feature.properties.customers_affected / 5),
                fillColor:
                  feature.properties.customers_affected > 10 ? 'red' : 'orange',
                fillOpacity: 0.7,
              }).bindPopup(`
                            <b>Incident:</b> ${feature.properties.incident_id}<br>
                            <b>Customers:</b> ${feature.properties.customers_affected}<br>
                            <b>Status:</b> ${feature.properties.status}
                        `);
            },
          }).addTo(map);

          document.getElementById(
            'stats'
          ).innerHTML = `<h3>${data.features.length} active outages</h3>`;
        } catch (error) {
          console.error('Error loading outages:', error);
          document.getElementById('stats').innerHTML =
            '<h3 style="color: red;">Error loading outage data</h3>';
        }
      }

      loadOutages();
      setInterval(loadOutages, 120000); // Refresh every 2 minutes
    </script>
  </body>
</html>
```

#### Command Line Tools

```bash
# Get current outage count
curl -s http://localhost:8000/outages/summary | jq '.total_outages'

# Get outages affecting 10+ customers
curl -s http://localhost:8000/outages | jq '.outages[] | select(.customers_affected >= 10)'

# Export current outages to CSV
curl -s http://localhost:8000/outages | jq -r '.outages[] | [.incident_id, .customers_affected, .status] | @csv'
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Import Errors

```bash
# Error: Could not import TECOUnifiedAPI
# Solution: Check file names match exactly
ls -la *.py
# Ensure you have: teco_fastapi.py, teco_uni_api.py, teco_ui.py

# Update import in teco_fastapi.py to match your filename
# from teco_uni_api import TECOUnifiedAPI
```

#### 2. Port Conflicts

```bash
# Error: Address already in use
# Solution: Use different ports
uvicorn teco_fastapi:app --host 0.0.0.0 --port 8001 --reload
streamlit run teco_ui.py --server.port 8502
```

#### 3. Connection Issues

```bash
# Test FastAPI health
curl http://localhost:8000/health

# Test with verbose output
curl -v http://localhost:8000/outages

# Check if services are running
ps aux | grep uvicorn
ps aux | grep streamlit
```

#### 4. Streamlit Cannot Connect to API

1. **Check FastAPI is running**: Visit http://localhost:8000/health
2. **Update API URL in Streamlit**: Use correct port in sidebar
3. **CORS Issues**: FastAPI includes CORS middleware for localhost

#### 5. No Polygon Data Displayed

- **Check debug mode** in Streamlit to see raw data structure
- **Verify TECO API response** includes `polygonPoints` fields
- **Check console logs** for polygon parsing messages

#### 6. Empty/No Outage Data

```json
{
  "summary": {
    "total_outages": 0,
    "total_customers_affected": 0
  }
}
```

This is normal when TECO has no current outages. Use "🧪 Load Test Data" in Streamlit to test with sample data.

### Debug Commands

#### Check Service Status

```bash
# Test FastAPI endpoints
curl http://localhost:8000/health
curl http://localhost:8000/outages/summary

# Check Streamlit is accessible
curl http://localhost:8501
```

#### Enable Debug Logging

```python
# Add to top of teco_fastapi.py for detailed logs
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Test TECO API Directly

```python
# Run this in Python to test core API
from teco_uni_api import TECOUnifiedAPI

api = TECOUnifiedAPI()
data = api.get_geo_tiles_with_polygons(size=5)
print(f"Retrieved {len(data.get('hits', {}).get('hits', []))} outages")
```

### Performance Issues

- **Slow responses**: Check TECO API status with `/health` endpoint
- **High memory usage**: Reduce cache TTL or limit outage size
- **Map loading slowly**: Try different tile layers in Streamlit

### Getting Help

1. **Check this documentation** for your specific issue
2. **Test the health endpoint**: `curl http://localhost:8000/health`
3. **Enable debug mode** in Streamlit to see raw data
4. **Check server logs** for detailed error messages

---

## 🤝 Contributing

### Development Setup

```bash
# Clone/download project files
mkdir teco-outage-api
cd teco-outage-api

# Install development dependencies
uv add fastapi uvicorn streamlit folium streamlit-folium pandas requests python-multipart pytest

# Run tests (if available)
pytest

# Start development servers
uvicorn teco_fastapi:app --reload &
streamlit run teco_ui.py &
```

### Project Architecture

#### Data Flow

1. **`teco_uni_api.py`** → Fetches data from TECO's Elasticsearch API
2. **`teco_fastapi.py`** → Provides RESTful interface with caching
3. **`teco_ui.py`** → Consumes API and displays interactive maps

#### Key Components

- **Authentication**: Automatic session key extraction from TECO
- **Data Preservation**: Complete raw data passed through all layers
- **Polygon Extraction**: Intelligent parsing of TECO's boundary data
- **Caching**: Smart caching to reduce API load

### Adding Features

#### New API Endpoints

Add to `teco_fastapi.py`:

```python
@app.get("/outages/new-feature")
async def new_feature():
    # Your implementation
    pass
```

#### New Streamlit Features

Add to `teco_ui.py`:

```python
# Add to sidebar
new_feature = st.sidebar.checkbox("New Feature")

# Add to main area
if new_feature:
    st.write("New feature content")
```

#### Enhance Core API

Modify `teco_uni_api.py`:

```python
def new_api_method(self):
    # Extend TECO API functionality
    pass
```

### Testing Your Changes

#### Test FastAPI Changes

```bash
# Test all endpoints
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/outages
curl http://localhost:8000/outages/summary
curl http://localhost:8000/outages/geojson
```

#### Test Streamlit Changes

1. Restart Streamlit: `streamlit run teco_ui.py`
2. Test with real data and test data
3. Verify map functionality and polygon display
4. Check debug mode output

#### Test Core API Changes

```python
# Test in Python
from teco_uni_api import TECOUnifiedAPI
api = TECOUnifiedAPI()
api.print_all_outages_detailed()
```

---

## 📋 Requirements.txt

Create a `requirements.txt` file with these dependencies:

```txt
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
streamlit>=1.28.0
folium>=0.15.0
streamlit-folium>=0.15.0
pandas>=2.0.0
requests>=2.31.0
python-multipart>=0.0.6
```

### Installing from Requirements

```bash
# Using uv
uv pip install -r requirements.txt

# Using pip
pip install -r requirements.txt
```

---

## 🔒 Security Considerations

### For Local Development

- **Default settings are secure** for local development
- **CORS enabled** for localhost connections
- **No authentication required** for local testing

### For Production Deployment

1. **Restrict CORS origins** in `teco_fastapi.py`:

   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],  # Specify your domain
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["*"],
   )
   ```

2. **Add rate limiting** for public APIs
3. **Use HTTPS** in production
4. **Monitor API usage** to prevent abuse
5. **Set up proper logging** and monitoring

### Responsible Usage

- **Respect TECO's servers**: The API includes rate limiting and caching
- **Don't abuse the service**: Cache responses appropriately
- **Monitor your usage**: Check health endpoints regularly
- **Follow TECO's terms**: Comply with TECO Energy's terms of service

---

## 📊 Performance Optimization

### Backend Optimization

```python
# Adjust cache TTL based on your needs
cache = {"data": None, "timestamp": None, "ttl_seconds": 300}  # 5 minutes

# Adjust rate limiting
api = TECOUnifiedAPI(rate_limit_delay=1.0)  # 1 second between requests

# Limit response size for better performance
response = api.get_geo_tiles_with_polygons(size=1000)  # Limit to 1000 outages
```

### Frontend Optimization

```python
# In Streamlit, adjust refresh intervals
refresh_interval = st.sidebar.slider(
    "Refresh interval (seconds)",
    min_value=60,    # Minimum 1 minute
    max_value=600,   # Maximum 10 minutes
    value=300        # Default 5 minutes
)

# Use caching for expensive operations
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_outage_data(api_url):
    return get_outage_data(api_url)
```

### Network Optimization

- **Use CDN** for static assets in production
- **Enable compression** in FastAPI
- **Implement proper caching headers**
- **Use connection pooling** for multiple requests

---

## 📚 Additional Resources

### TECO Energy Resources

- **Official Outage Map**: https://outage.tecoenergy.com/
- **TECO Website**: https://www.tecoenergy.com/
- **Service Area**: Tampa Bay, Florida region

### Technical Documentation

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Streamlit Docs**: https://docs.streamlit.io/
- **Folium Docs**: https://python-visualization.github.io/folium/
- **Uvicorn Docs**: https://www.uvicorn.org/

### GIS and Mapping Resources

- **Leaflet**: https://leafletjs.com/
- **GeoJSON Specification**: https://geojson.org/
- **WGS84 Coordinate System**: https://en.wikipedia.org/wiki/World_Geodetic_System

### Python Package Managers

- **uv**: https://github.com/astral-sh/uv (Recommended)
- **pip**: https://pip.pypa.io/en/stable/
- **conda**: https://docs.conda.io/en/latest/

---

## 🚀 What's Next?

### Planned Features

- **Historical data analysis** and trending
- **Alert system** for major outages
- **Mobile app** development
- **Integration with other utility APIs**
- **Advanced GIS analysis** capabilities
- **Real-time notifications** via email/SMS

### Community Contributions

We welcome contributions for:

- **Additional utility APIs** (FPL, Duke Energy, etc.)
- **Enhanced visualizations** and charts
- **Mobile-responsive improvements**
- **Performance optimizations**
- **Documentation improvements**

### Feedback and Support

- **Report issues** with detailed error messages
- **Suggest features** for future development
- **Share use cases** and success stories
- **Contribute code** improvements and bug fixes

---

## 📝 License

This project is provided as-is for educational and personal use. Please be respectful of TECO Energy's resources and comply with their terms of service.

### Usage Guidelines

- ✅ **Personal use** and learning
- ✅ **Academic research** and analysis
- ✅ **Emergency preparedness** planning
- ❌ **Commercial redistribution** without permission
- ❌ **Excessive API usage** that could impact TECO's services
- ❌ **Violation of TECO's terms** of service

---

## 📞 Support & Contact

### Getting Help

#### 1. Self-Service Troubleshooting

- **Check this README** for common issues and solutions
- **Test health endpoints** to verify system status
- **Enable debug mode** in Streamlit for detailed information
- **Review server logs** for error messages

#### 2. System Status Checks

```bash
# Verify FastAPI is running
curl http://localhost:8000/health

# Check Streamlit accessibility
curl http://localhost:8501

# Test TECO API connectivity
curl http://localhost:8000/outages/summary
```

#### 3. Common Solutions

- **Restart services** if they become unresponsive
- **Clear API cache** if data seems stale: `curl -X POST http://localhost:8000/cache/clear`
- **Check network connectivity** to TECO's servers
- **Verify file permissions** and Python environment

### Development Support

- **Source code** is fully documented with inline comments
- **API documentation** available at http://localhost:8000/docs
- **Debug mode** in Streamlit shows raw data structures
- **Health checks** provide system status information

### Production Deployment Help

- **Railway.app**: Follow their FastAPI deployment guides
- **Streamlit Cloud**: Use their GitHub integration
- **Docker**: Reference provided Dockerfile examples
- **VPS**: Standard Python/FastAPI deployment practices

---

## 🎉 Quick Success Checklist

Use this checklist to verify your installation is working correctly:

### ✅ Installation Checklist

- [ ] Python 3.8+ installed
- [ ] All files downloaded (teco_fastapi.py, teco_uni_api.py, teco_ui.py)
- [ ] Dependencies installed via uv or pip
- [ ] No import errors when starting applications

### ✅ FastAPI Backend Checklist

- [ ] Server starts without errors: `uvicorn teco_fastapi:app --reload`
- [ ] Health check works: `curl http://localhost:8000/health`
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Outages endpoint returns data: `curl http://localhost:8000/outages/summary`

### ✅ Streamlit Frontend Checklist

- [ ] App starts successfully: `streamlit run teco_ui.py`
- [ ] Interface loads at http://localhost:8501
- [ ] Test data loads: Click "🧪 Load Test Data"
- [ ] Map displays with markers and polygons
- [ ] API endpoint connects: Default `http://localhost:8000/outages` works

### ✅ Integration Checklist

- [ ] Streamlit can fetch data from FastAPI
- [ ] Real polygon boundaries display (when outages exist)
- [ ] Debug mode shows raw data structure
- [ ] Map interactions work (click markers/polygons)
- [ ] Statistics update correctly

### 🎯 Success Indicators

When everything is working correctly, you should see:

1. **FastAPI Console**:

   ```
   INFO: Started server process [12345]
   INFO: Application startup complete.
   INFO: Uvicorn running on http://0.0.0.0:8000
   ```

2. **Streamlit Interface**:

   - Map centered on Tampa Bay area
   - Live statistics showing current outages
   - Clickable markers with popup information
   - Service area polygons (actual TECO boundaries when available)

3. **API Responses**:
   - JSON data with outage information
   - `raw_geo_data` containing polygon coordinates
   - Proper HTTP status codes (200 for success)

**Congratulations!** 🎉 You now have a complete TECO Energy outage monitoring system running locally.

---

## 📈 Version History

### Current Version: 1.0.0

- ✅ Complete FastAPI backend with caching and authentication
- ✅ Streamlit web interface with interactive maps
- ✅ Real TECO service area polygon extraction and display
- ✅ Multiple data formats (JSON, GeoJSON, raw Elasticsearch)
- ✅ Comprehensive documentation and examples
- ✅ Docker and cloud deployment support

### Future Versions

- **1.1.0**: Historical data analysis and trending
- **1.2.0**: Mobile app and responsive design improvements
- **1.3.0**: Multi-utility support (FPL, Duke Energy, etc.)
- **2.0.0**: Advanced GIS analysis and alert systems

---

_This documentation was last updated on July 18, 2025. For the most current information, please check the project repository._

**Happy mapping! 🗺️⚡**
