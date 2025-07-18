"""
TECO Energy Outage API Server
FastAPI wrapper for TECO outage data

Installation:
pip install fastapi uvicorn python-multipart

Usage:
uvicorn teco_fastapi:app --host 0.0.0.0 --port 8000 --reload

API Endpoints:
- GET /outages - Get all current outages
- GET /outages/summary - Get summary statistics
- GET /outages/bbox - Get outages in bounding box
- GET /health - Health check
- GET /docs - API documentation
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import time
from datetime import datetime, timedelta
import logging

# Import your TECO API class (assuming it's in the same directory)
try:
    from teco_uni_api import TECOUnifiedAPI

except ImportError:
    # If the import fails, we'll create a minimal version for demo
    print("⚠️  Could not import TECOUnifiedAPI - using mock data for demo")

    class TECOUnifiedAPI:
        def get_geo_tiles(self, **kwargs):
            return {
                "hits": {"hits": [], "total": {"value": 0}},
                "aggregations": {"customerCountSum": {"value": 0}},
            }


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="TECO Energy Outage API",
    description="Real-time power outage data for TECO Energy service area",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# Pydantic models for API responses
class OutageLocation(BaseModel):
    lat: float
    lon: float


class RawGeoData(BaseModel):
    """Raw geographic/GIS data from TECO API"""

    polygon_center: List[float]  # [longitude, latitude]
    elasticsearch_id: str
    elasticsearch_index: str
    raw_source: Dict[str, Any]  # Complete _source data


class TilesMetadata(BaseModel):
    """Raw tiles information for GIS applications"""

    requested: Optional[int] = None
    with_data: Optional[int] = None
    zoom: Optional[int] = None
    index_name: Optional[str] = None
    generated: Optional[str] = None
    performance: Optional[Dict[str, Any]] = None


class Outage(BaseModel):
    incident_id: str
    location: OutageLocation
    customers_affected: int
    status: str
    reason: str
    last_updated: str
    estimated_restoration: Optional[str] = None
    # NEW: Include raw GIS data
    raw_geo_data: RawGeoData


class OutageSummary(BaseModel):
    total_outages: int
    total_customers_affected: int
    last_updated: str
    data_source: str


class OutageResponse(BaseModel):
    summary: OutageSummary
    outages: List[Outage]
    metadata: Dict[str, Any]
    # NEW: Include raw tiles and GIS data
    raw_tiles_data: Optional[TilesMetadata] = None
    raw_elasticsearch_response: Optional[Dict[str, Any]] = None


class BoundingBox(BaseModel):
    north: float = Query(..., description="Northern latitude boundary")
    south: float = Query(..., description="Southern latitude boundary")
    east: float = Query(..., description="Eastern longitude boundary")
    west: float = Query(..., description="Western longitude boundary")


# Cache for API responses (simple in-memory cache)
cache = {"data": None, "timestamp": None, "ttl_seconds": 300}  # 5 minutes


def is_cache_valid() -> bool:
    """Check if cached data is still valid"""
    if not cache["data"] or not cache["timestamp"]:
        return False

    age = datetime.now() - cache["timestamp"]
    return age.total_seconds() < cache["ttl_seconds"]


async def get_fresh_outage_data(bbox_params: Optional[Dict] = None) -> Dict:
    """Get fresh outage data from TECO API"""
    try:
        # Run TECO API in thread pool to avoid blocking
        loop = asyncio.get_event_loop()

        def fetch_data():
            # Initialize without parameters (some versions don't accept rate_limit_delay)
            try:
                api = TECOUnifiedAPI(rate_limit_delay=0.5)
            except TypeError:
                # Fallback if constructor doesn't accept rate_limit_delay
                api = TECOUnifiedAPI()

            if bbox_params:
                # Try the enhanced method first, fall back to original
                if hasattr(api, "get_geo_tiles_with_polygons"):
                    return api.get_geo_tiles_with_polygons(**bbox_params)
                elif hasattr(api, "get_geo_tiles"):
                    return api.get_geo_tiles(**bbox_params)
                else:
                    # Create a minimal response for demo
                    return {
                        "hits": {"hits": [], "total": {"value": 0}},
                        "aggregations": {"customerCountSum": {"value": 0}},
                    }
            else:
                # Try the enhanced method first, fall back to original
                if hasattr(api, "get_geo_tiles_with_polygons"):
                    return api.get_geo_tiles_with_polygons()
                elif hasattr(api, "get_geo_tiles"):
                    return api.get_geo_tiles()
                else:
                    # Create a minimal response for demo
                    return {
                        "hits": {"hits": [], "total": {"value": 0}},
                        "aggregations": {"customerCountSum": {"value": 0}},
                    }

        # Execute in thread pool
        data = await loop.run_in_executor(None, fetch_data)

        if not data:
            raise Exception("Failed to fetch data from TECO API")

        return data

    except Exception as e:
        logger.error(f"Error fetching TECO data: {e}")
        raise HTTPException(
            status_code=503, detail=f"Failed to fetch outage data: {str(e)}"
        )


def transform_teco_data(raw_data: Dict) -> OutageResponse:
    """Transform TECO API response to our standardized format while preserving raw GIS data"""
    try:
        hits = raw_data.get("hits", {}).get("hits", [])
        total_customers = (
            raw_data.get("aggregations", {}).get("customerCountSum", {}).get("value", 0)
        )
        tiles_info = raw_data.get("_tiles", {})

        # Transform individual outages with FULL GIS data preservation
        outages = []
        for hit in hits:
            source = hit.get("_source", {})
            polygon_center = source.get("polygonCenter", [0, 0])

            # Create raw geo data object with ALL original information
            raw_geo_data = RawGeoData(
                polygon_center=polygon_center,
                elasticsearch_id=hit.get("_id", ""),
                elasticsearch_index=hit.get("_index", ""),
                raw_source=source,  # Complete original source data
            )

            # Create simplified location for easy access
            location = OutageLocation(
                lat=polygon_center[1] if len(polygon_center) >= 2 else 0,
                lon=polygon_center[0] if len(polygon_center) >= 2 else 0,
            )

            outage = Outage(
                incident_id=source.get("incidentId", ""),
                location=location,
                customers_affected=source.get("customerCount", 0),
                status=source.get("status", "Unknown"),
                reason=source.get("reason", "Unknown"),
                last_updated=source.get("updateTime", ""),
                estimated_restoration=source.get("estimatedTimeOfRestoration"),
                raw_geo_data=raw_geo_data,  # Include complete raw GIS data
            )
            outages.append(outage)

        # Create tiles metadata for GIS applications
        raw_tiles_data = TilesMetadata(
            requested=tiles_info.get("requested"),
            with_data=tiles_info.get("withData"),
            zoom=tiles_info.get("zoom"),
            index_name=tiles_info.get("indexName"),
            generated=tiles_info.get("generated"),
            performance=tiles_info.get("performance"),
        )

        # Create summary
        summary = OutageSummary(
            total_outages=len(outages),
            total_customers_affected=total_customers,
            last_updated=datetime.now().isoformat(),
            data_source="TECO Energy",
        )

        # Create metadata with GIS information
        metadata = {
            "query_time": datetime.now().isoformat(),
            "data_freshness": "real-time",
            "api_version": "1.0.0",
            "source_api": "TECO Energy Outage Map",
            "gis_info": {
                "coordinate_system": "WGS84 (EPSG:4326)",
                "polygon_center_format": "[longitude, latitude]",
                "elasticsearch_backend": True,
                "tiles_zoom_level": tiles_info.get("zoom"),
                "spatial_index": tiles_info.get("indexName"),
            },
            "cache_info": {"cached": False, "ttl_seconds": cache["ttl_seconds"]},
        }

        return OutageResponse(
            summary=summary,
            outages=outages,
            metadata=metadata,
            raw_tiles_data=raw_tiles_data,  # Include raw tiles data
            raw_elasticsearch_response=raw_data,  # Include complete raw response
        )

    except Exception as e:
        logger.error(f"Error transforming data: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error processing outage data: {str(e)}"
        )


@app.get("/", tags=["Info"])
async def root():
    """API root endpoint with basic info"""
    return {
        "name": "TECO Energy Outage API",
        "version": "1.0.0",
        "description": "Real-time power outage data for TECO Energy service area",
        "endpoints": {
            "outages": "/outages - Get all current outages",
            "summary": "/outages/summary - Get summary statistics",
            "bbox": "/outages/bbox - Get outages in bounding box",
            "health": "/health - Health check",
            "docs": "/docs - API documentation",
        },
        "data_source": "TECO Energy Outage Map",
        "cache_ttl": f"{cache['ttl_seconds']} seconds",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Quick test of TECO API availability
        try:
            api = TECOUnifiedAPI(rate_limit_delay=0)
        except TypeError:
            # Fallback if constructor doesn't accept rate_limit_delay
            api = TECOUnifiedAPI()

        # Try different methods based on availability
        test_data = None
        if hasattr(api, "get_geo_tiles_with_polygons"):
            test_data = api.get_geo_tiles_with_polygons(size=1)
        elif hasattr(api, "get_geo_tiles"):
            test_data = api.get_geo_tiles(size=1)

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "teco_api_available": test_data is not None,
            "cache_valid": is_cache_valid(),
            "api_methods_available": {
                "get_geo_tiles": hasattr(api, "get_geo_tiles"),
                "get_geo_tiles_with_polygons": hasattr(
                    api, "get_geo_tiles_with_polygons"
                ),
                "analyze_polygon_data": hasattr(api, "analyze_polygon_data"),
            },
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
        )


@app.get("/outages", response_model=OutageResponse, tags=["Outages"])
async def get_all_outages(
    use_cache: bool = Query(True, description="Use cached data if available"),
    size: int = Query(10000, description="Maximum number of outages to return"),
):
    """
    Get all current power outages in TECO's service area

    Returns comprehensive outage data including:
    - Individual outage details with locations
    - Summary statistics
    - Metadata about data freshness
    """

    # Check cache first
    if use_cache and is_cache_valid():
        logger.info("Returning cached outage data")
        response = cache["data"]
        response.metadata["cache_info"]["cached"] = True
        return response

    # Fetch fresh data
    logger.info("Fetching fresh outage data from TECO API")
    raw_data = await get_fresh_outage_data({"size": size})
    response = transform_teco_data(raw_data)

    # Update cache
    cache["data"] = response
    cache["timestamp"] = datetime.now()

    return response


@app.get("/outages/summary", response_model=OutageSummary, tags=["Outages"])
async def get_outage_summary(
    use_cache: bool = Query(True, description="Use cached data if available")
):
    """
    Get summary statistics of current outages

    Returns:
    - Total number of outages
    - Total customers affected
    - Last updated timestamp
    """

    outage_data = await get_all_outages(use_cache=use_cache, size=1000)
    return outage_data.summary


@app.get("/outages/bbox", response_model=OutageResponse, tags=["Outages"])
async def get_outages_by_bbox(
    north: float = Query(..., description="Northern latitude boundary", example=28.7),
    south: float = Query(..., description="Southern latitude boundary", example=27.0),
    east: float = Query(..., description="Eastern longitude boundary", example=-79.9),
    west: float = Query(..., description="Western longitude boundary", example=-84.7),
    size: int = Query(10000, description="Maximum number of outages to return"),
):
    """
    Get outages within a specified bounding box

    Allows filtering outages by geographic area using latitude/longitude boundaries.
    Useful for focusing on specific regions or cities.
    """

    bbox_params = {
        "top_left_lat": north,
        "top_left_lon": west,
        "bottom_right_lat": south,
        "bottom_right_lon": east,
        "size": size,
    }

    logger.info(f"Fetching outages for bounding box: N{north} S{south} E{east} W{west}")
    raw_data = await get_fresh_outage_data(bbox_params)
    return transform_teco_data(raw_data)


@app.get("/outages/raw", tags=["GIS Data"])
async def get_raw_outage_data(
    use_cache: bool = Query(True, description="Use cached data if available"),
    size: int = Query(10000, description="Maximum number of outages to return"),
):
    """
    Get raw, unprocessed outage data from TECO's Elasticsearch API

    Returns the complete, unmodified response from TECO's backend including:
    - Full Elasticsearch document structure
    - Raw polygon/geometry data
    - Complete tiles metadata
    - All original field names and values

    Ideal for GIS applications that need the original spatial data format.
    """

    raw_data = await get_fresh_outage_data({"size": size})

    return {
        "data_source": "TECO Energy Elasticsearch API",
        "format": "Raw Elasticsearch Response",
        "coordinate_system": "WGS84 (EPSG:4326)",
        "polygon_format": "Center point as [longitude, latitude]",
        "timestamp": datetime.now().isoformat(),
        "raw_response": raw_data,
    }


@app.get("/outages/geojson", tags=["GIS Data"])
async def get_outages_as_geojson(
    use_cache: bool = Query(True, description="Use cached data if available"),
    size: int = Query(10000, description="Maximum number of outages to return"),
):
    """
    Get outage data formatted as GeoJSON for mapping applications

    Returns outages in standard GeoJSON format with:
    - Point geometries at outage locations
    - All outage properties in the properties object
    - Compatible with Leaflet, Mapbox, QGIS, etc.
    """

    # Get the processed data first
    outage_data = await get_all_outages(use_cache=use_cache, size=size)

    # Convert to GeoJSON format
    features = []
    for outage in outage_data.outages:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    outage.location.lon,
                    outage.location.lat,
                ],  # GeoJSON uses [lon, lat]
            },
            "properties": {
                "incident_id": outage.incident_id,
                "customers_affected": outage.customers_affected,
                "status": outage.status,
                "reason": outage.reason,
                "last_updated": outage.last_updated,
                "estimated_restoration": outage.estimated_restoration,
                # Include raw data for advanced users
                "elasticsearch_id": outage.raw_geo_data.elasticsearch_id,
                "elasticsearch_index": outage.raw_geo_data.elasticsearch_index,
                "polygon_center": outage.raw_geo_data.polygon_center,
            },
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "metadata": {
            "generated": datetime.now().isoformat(),
            "count": len(features),
            "data_source": "TECO Energy",
            "coordinate_system": "WGS84 (EPSG:4326)",
        },
        "features": features,
    }

    return geojson


async def get_outage_by_incident(incident_id: str):
    """
    Get details for a specific outage incident
    """

    outage_data = await get_all_outages(use_cache=True, size=10000)

    for outage in outage_data.outages:
        if outage.incident_id == incident_id:
            return {
                "incident": outage,
                "found": True,
                "timestamp": datetime.now().isoformat(),
            }

    raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")


@app.get("/debug/teco-raw", tags=["Debug"])
async def debug_teco_raw():
    """
    Debug endpoint to test direct TECO API connection
    """
    try:
        # Initialize API
        try:
            api = TECOUnifiedAPI(rate_limit_delay=0)
        except TypeError:
            api = TECOUnifiedAPI()

        # Test different methods and show results
        debug_info = {
            "timestamp": datetime.now().isoformat(),
            "config_status": None,
            "original_method_result": None,
            "enhanced_method_result": None,
            "available_methods": {
                "get_geo_tiles": hasattr(api, "get_geo_tiles"),
                "get_geo_tiles_with_polygons": hasattr(
                    api, "get_geo_tiles_with_polygons"
                ),
                "analyze_polygon_data": hasattr(api, "analyze_polygon_data"),
            },
        }

        # Test config loading
        if hasattr(api, "config"):
            debug_info["config_status"] = {
                "config_loaded": api.config is not None,
                "session_key_available": hasattr(api, "_fresh_session_key")
                and api._fresh_session_key is not None,
            }
            if api.config:
                debug_info["config_sample"] = {
                    "keys": list(api.config.keys())[:10],  # First 10 keys
                    "index": api.config.get("index", "Not found"),
                }

        # Test original method
        if hasattr(api, "get_geo_tiles"):
            try:
                result = api.get_geo_tiles(size=5)  # Small test
                debug_info["original_method_result"] = {
                    "success": result is not None,
                    "data_type": type(result).__name__,
                    "keys": (
                        list(result.keys())
                        if result and isinstance(result, dict)
                        else None
                    ),
                    "hits_count": (
                        result.get("hits", {}).get("total", {}).get("value")
                        if result
                        else None
                    ),
                    "sample_hit": (
                        result.get("hits", {}).get("hits", [{}])[0]
                        if result and result.get("hits", {}).get("hits")
                        else None
                    ),
                }
            except Exception as e:
                debug_info["original_method_result"] = {"error": str(e)}

        # Test enhanced method
        if hasattr(api, "get_geo_tiles_with_polygons"):
            try:
                result = api.get_geo_tiles_with_polygons(size=5)  # Small test
                debug_info["enhanced_method_result"] = {
                    "success": result is not None,
                    "data_type": type(result).__name__,
                    "keys": (
                        list(result.keys())
                        if result and isinstance(result, dict)
                        else None
                    ),
                    "hits_count": (
                        result.get("hits", {}).get("total", {}).get("value")
                        if result
                        else None
                    ),
                }
            except Exception as e:
                debug_info["enhanced_method_result"] = {"error": str(e)}

        return debug_info

    except Exception as e:
        return {"error": f"Debug failed: {str(e)}"}


@app.get("/debug/manual-test", tags=["Debug"])
async def debug_manual_test():
    """
    Manual test of TECO API without using TECOUnifiedAPI class
    """
    import requests

    try:
        # Test the config endpoint directly
        config_url = (
            "https://outage-data-prod-hrcadje2h9aje9c9.a03.azurefd.net/api/v1/config"
        )
        headers = {
            "Origin": "https://outage.tecoenergy.com",
            "Referer": "https://outage.tecoenergy.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        config_response = requests.get(config_url, headers=headers, timeout=10)

        debug_info = {
            "config_test": {
                "status_code": config_response.status_code,
                "success": config_response.status_code == 200,
                "headers": dict(config_response.headers),
                "config_data": (
                    config_response.json()
                    if config_response.status_code == 200
                    else None
                ),
            }
        }

        # Extract session key
        session_key = None
        if "set-cookie" in config_response.headers:
            set_cookie = config_response.headers["set-cookie"]
            if "MIC-X-API-V2=" in set_cookie:
                session_key = set_cookie.split("MIC-X-API-V2=")[1].split(";")[0]

        debug_info["session_key_extracted"] = session_key is not None

        if session_key:
            # Test outage tiles endpoint
            tiles_url = "https://outage-data-prod-hrcadje2h9aje9c9.a03.azurefd.net/api/v1/outage-tiles"
            tiles_headers = {
                **headers,
                "Content-Type": "application/json",
                "Cookie": f"MIC-X-API-V2={session_key}",
            }

            payload = {
                "size": 10,
                "query": {
                    "bool": {
                        "must": {"match_all": {}},
                        "filter": {
                            "geo_bounding_box": {
                                "polygonCenter": {
                                    "top_left": {"lat": 28.7, "lon": -84.7},
                                    "bottom_right": {"lat": 27.0, "lon": -79.9},
                                }
                            }
                        },
                    }
                },
                "sort": [{"updateTime": "asc"}],
                "_source": ["*"],  # Get all fields
            }

            tiles_response = requests.post(
                tiles_url, headers=tiles_headers, json=payload, timeout=10
            )

            debug_info["tiles_test"] = {
                "status_code": tiles_response.status_code,
                "success": tiles_response.status_code == 200,
                "response_data": (
                    tiles_response.json()
                    if tiles_response.status_code == 200
                    else tiles_response.text
                ),
            }

        return debug_info

    except Exception as e:
        return {"error": f"Manual test failed: {str(e)}"}


async def clear_cache():
    """
    Clear the API cache (forces fresh data on next request)
    """
    cache["data"] = None
    cache["timestamp"] = None

    return {
        "message": "Cache cleared successfully",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/stats", tags=["Info"])
async def get_api_stats():
    """
    Get API usage statistics and system info
    """
    return {
        "cache_status": {
            "valid": is_cache_valid(),
            "last_updated": (
                cache["timestamp"].isoformat() if cache["timestamp"] else None
            ),
            "ttl_seconds": cache["ttl_seconds"],
        },
        "api_info": {
            "version": "1.0.0",
            "uptime": "N/A",  # Would need startup tracking
            "total_requests": "N/A",  # Would need request counter
        },
        "timestamp": datetime.now().isoformat(),
    }


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat(),
        },
    )


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting TECO Outage API Server...")
    print("📖 Documentation will be available at: http://localhost:8000/docs")
    print("🔗 API root: http://localhost:8000/")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
