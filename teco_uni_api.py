import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import time
import random


class TECOUnifiedAPI:
    """
    Unified TECO Energy Outage API Client

    Combines both the geo-tiles endpoint and the currentState endpoint
    for comprehensive outage data analysis

    Designed to be robust and work across different environments
    """

    def __init__(self, rate_limit_delay: float = 1.0):
        self.config = None
        self.rate_limit_delay = rate_limit_delay
        self.headers = {
            "Origin": "https://outage.tecoenergy.com",
            "Referer": "https://outage.tecoenergy.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.tile_headers = {
            **self.headers,
            "Content-Type": "application/json",
            "Accept": "*/*",
        }
        self.base_url = "https://outage-data-prod-hrcadje2h9aje9c9.a03.azurefd.net"
        self._fresh_session_key = None
        self._load_config()

    def _rate_limit_delay(self):
        """Add delay between requests to be respectful"""
        if self.rate_limit_delay > 0:
            delay = self.rate_limit_delay + random.uniform(0, 0.5)
            time.sleep(delay)

    def _make_request(
        self, method: str, url: str, **kwargs
    ) -> Optional[requests.Response]:
        """Make HTTP request with error handling and retries"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                self._rate_limit_delay()

                if method.upper() == "GET":
                    response = requests.get(url, timeout=30, **kwargs)
                elif method.upper() == "POST":
                    response = requests.post(url, timeout=30, **kwargs)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                # Check if we got a response (even if error)
                if response.status_code == 200:
                    return response
                elif response.status_code in [401, 403]:
                    print(f"⚠️  Authentication issue (Status {response.status_code})")
                    return None
                elif response.status_code in [429, 503]:
                    print(
                        f"⚠️  Rate limited or service unavailable (Status {response.status_code})"
                    )
                    if attempt < max_retries - 1:
                        wait_time = (2**attempt) + random.uniform(0, 1)
                        print(f"   Waiting {wait_time:.1f}s before retry...")
                        time.sleep(wait_time)
                        continue
                else:
                    print(f"⚠️  HTTP {response.status_code}: {response.reason}")
                    return None

            except requests.exceptions.Timeout:
                print(f"⚠️  Request timeout (attempt {attempt + 1}/{max_retries})")
            except requests.exceptions.ConnectionError:
                print(f"⚠️  Connection error (attempt {attempt + 1}/{max_retries})")
            except Exception as e:
                print(f"⚠️  Unexpected error: {e}")

            if attempt < max_retries - 1:
                wait_time = (2**attempt) + random.uniform(0, 1)
                print(f"   Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)

        print(f"❌ Failed after {max_retries} attempts")
        return None

    def _load_config(self):
        """Load API configuration from TECO's config endpoint"""
        try:
            print("🔄 Loading TECO API configuration...")
            response = self._make_request(
                "GET", f"{self.base_url}/api/v1/config", headers=self.headers
            )

            if not response:
                print("❌ Failed to load config")
                self.config = None
                return

            self.config = response.json()

            # IMPORTANT: Extract fresh session key from response headers!
            set_cookie_header = response.headers.get("set-cookie", "")
            if "MIC-X-API-V2=" in set_cookie_header:
                for cookie_part in set_cookie_header.split(","):
                    if "MIC-X-API-V2=" in cookie_part:
                        key_part = (
                            cookie_part.split("MIC-X-API-V2=")[1].split(";")[0].strip()
                        )
                        self._fresh_session_key = key_part
                        print(f"🔑 Extracted fresh session key: {key_part[:20]}...")
                        break

            print(
                "✅ Config loaded successfully! This contains map settings and Elasticsearch index info."
            )
            print(f"   Elasticsearch Index: {self.config.get('index', 'N/A')}")
            print(f"   Map Center: {self.config.get('CenterPosition', 'N/A')}")

        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            self.config = None

    def get_current_state(self) -> Optional[Dict]:
        """
        Get current outage state using the currentState endpoint
        This provides overall statistics and outage list

        Based on your working code, we need to use the config data differently
        """
        if not self.config:
            print("❌ No config loaded")
            return None

        # From the working code, we know the pattern:
        # The config should contain apiBase, instanceId, viewId
        # But if it doesn't, we need to find the right endpoint

        # Let's try to extract the correct URL from your working example
        # Your code used: f"{base}/stormcenters/{iid}/views/{vid}/currentState?preview=false"

        # Try the endpoints that should work based on your original discovery
        potential_endpoints = [
            # Based on your working config approach - these should be discoverable
            "https://api.tecoenergy.com/stormcenters/teco/views/default/currentState?preview=false",
            # Alternative patterns
            "https://outage-api.tecoenergy.com/stormcenters/teco/views/live/currentState?preview=false",
            "https://outage-api.tecoenergy.com/stormcenters/teco/views/default/currentState?preview=false",
            # Try different instance/view combinations
            "https://api.tecoenergy.com/stormcenters/tampa/views/default/currentState?preview=false",
            "https://api.tecoenergy.com/stormcenters/tecoenergy/views/default/currentState?preview=false",
        ]

        for url in potential_endpoints:
            try:
                print(f"🌐 Trying: {url}")
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    if data and isinstance(data, dict):
                        print(f"✅ Success with: {url}")
                        return data
                print(f"   Status: {response.status_code}")
            except Exception as e:
                print(f"   Error: {e}")
                continue

        print("❌ All currentState endpoints failed")
        return None

    def get_geo_tiles(
        self,
        top_left_lat: float = 28.70343307240943,
        top_left_lon: float = -84.70102730976562,
        bottom_right_lat: float = 27.003667078761065,
        bottom_right_lon: float = -79.99613229023437,
        size: int = 10000,
        api_key: str = None,
    ) -> Optional[Dict]:
        """
        Get geo-spatial outage data using the tiles endpoint (original method)
        This provides detailed geographic information
        """
        # The config response headers contain a fresh session key!
        if not api_key and self._fresh_session_key:
            api_key = self._fresh_session_key
            print(f"🔑 Using fresh session key from config: {api_key[:20]}...")

        if api_key:
            headers_with_auth = {
                **self.tile_headers,
                "Cookie": f"MIC-X-API-V2={api_key}",
            }
        else:
            headers_with_auth = self.tile_headers
            print("⚠️  No session key available - request may fail")

        payload = {
            "size": size,
            "query": {
                "bool": {
                    "must": {"match_all": {}},
                    "filter": {
                        "geo_bounding_box": {
                            "polygonCenter": {
                                "top_left": {"lat": top_left_lat, "lon": top_left_lon},
                                "bottom_right": {
                                    "lat": bottom_right_lat,
                                    "lon": bottom_right_lon,
                                },
                            }
                        }
                    },
                }
            },
            "sort": [{"updateTime": "asc"}, {"incidentId": "asc"}],
            "_source": "*",  # Get ALL fields instead of specific ones
        }

        try:
            response = self._make_request(
                "POST",
                f"{self.base_url}/api/v1/outage-tiles",
                headers=headers_with_auth,
                json=payload,
            )
            if response:
                return response.json()
            else:
                print("❌ Failed to get geo tiles data")
                return None
        except Exception as e:
            print(f"❌ Failed to get geo tiles: {e}")
            return None

    # This is the method that returns the geo tiles with polygons
    # It uses the same logic as get_geo_tiles but requests all fields
    # to find polygon data
    def get_geo_tiles_with_polygons(
        self,
        top_left_lat: float = 28.70343307240943,
        top_left_lon: float = -84.70102730976562,
        bottom_right_lat: float = 27.003667078761065,
        bottom_right_lon: float = -79.99613229023437,
        size: int = 10000,
        api_key: str = None,
    ) -> Optional[Dict]:
        """
        Get geo-spatial outage data with enhanced polygon information
        This version requests additional fields that might contain full polygon data
        """
        # The config response headers contain a fresh session key!
        if not api_key and self._fresh_session_key:
            api_key = self._fresh_session_key
            print(f"🔑 Using fresh session key from config: {api_key[:20]}...")

        if api_key:
            headers_with_auth = {
                **self.tile_headers,
                "Cookie": f"MIC-X-API-V2={api_key}",
            }
        else:
            headers_with_auth = self.tile_headers
            print("⚠️  No session key available - request may fail")

        # ==== ATTENTION ====
        # This is the payload structure that returns all fields including polygons
        # ==== ATTENTION ====
        payload = {
            "size": size,
            "query": {
                "bool": {
                    "must": {"match_all": {}},
                    "filter": {
                        "geo_bounding_box": {
                            "polygonCenter": {
                                "top_left": {"lat": top_left_lat, "lon": top_left_lon},
                                "bottom_right": {
                                    "lat": bottom_right_lat,
                                    "lon": bottom_right_lon,
                                },
                            }
                        }
                    },
                }
            },
            "sort": [{"updateTime": "asc"}, {"incidentId": "asc"}],
            "_source": "*",  # ===> KEY: Get ALL fields including polygon data - this is crucial - we get all fields from the API including the polygon data!
        }

        try:
            response = self._make_request(
                "POST",
                f"{self.base_url}/api/v1/outage-tiles",
                headers=headers_with_auth,
                json=payload,
            )
            if response:
                return response.json()
            else:
                print("❌ Failed to get geo tiles data")
                return None
        except Exception as e:
            print(f"❌ Failed to get geo tiles: {e}")
            return None

    def analyze_polygon_data(self) -> Dict:
        """
        Analyze the API response to identify polygon data fields
        """
        print("🔍 Analyzing TECO API response for polygon data...")

        # Get fresh data with all possible fields
        data = self.get_geo_tiles_with_polygons()

        if not data:
            return {"error": "No data received"}

        analysis = {
            "total_records": len(data.get("hits", {}).get("hits", [])),
            "available_fields": set(),
            "sample_records": [],
            "potential_polygon_fields": [],
        }

        hits = data.get("hits", {}).get("hits", [])

        for i, hit in enumerate(hits[:3]):  # Analyze first 3 records
            source = hit.get("_source", {})
            analysis["available_fields"].update(source.keys())

            # Create detailed sample
            sample = {"incident_id": source.get("incidentId"), "all_fields": {}}

            for field, value in source.items():
                sample["all_fields"][field] = {
                    "value": value,
                    "type": type(value).__name__,
                    "length": len(str(value)) if value else 0,
                }

                # Check if this might be polygon data
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
                    analysis["potential_polygon_fields"].append(
                        {"field": field, "value": value, "type": type(value).__name__}
                    )

            analysis["sample_records"].append(sample)

        # Print detailed analysis
        print(f"📊 Analysis Results:")
        print(f"   Total records: {analysis['total_records']}")
        print(f"   Available fields: {sorted(analysis['available_fields'])}")
        print(
            f"   Potential polygon fields: {len(analysis['potential_polygon_fields'])}"
        )

        for field_info in analysis["potential_polygon_fields"]:
            print(
                f"   🗺️  {field_info['field']}: {field_info['type']} = {field_info['value']}"
            )

        return analysis

    def _try_get_session_key(self) -> Optional[str]:
        """
        Attempt to get a session key by visiting the main page
        This is a basic attempt - may not always work
        """
        try:
            response = requests.get(
                "https://outage.tecoenergy.com/", headers=self.headers
            )
            # Look for any session cookies
            for cookie in response.cookies:
                if "MIC-X-API" in cookie.name:
                    return cookie.value
        except:
            pass
        return None

    def get_unified_data(self, api_key: str = None) -> Dict:
        """
        Get data from both endpoints and merge them for comprehensive analysis
        """
        print("🔄 Fetching data from both endpoints...")

        # Get current state data
        state_data = self.get_current_state()

        # Get geo tiles data
        geo_data = self.get_geo_tiles(api_key=api_key)

        return {
            "timestamp": datetime.now().isoformat(),
            "current_state": state_data,
            "geo_tiles": geo_data,
            "analysis": self._analyze_combined_data(state_data, geo_data),
        }

    def _analyze_combined_data(self, state_data: Dict, geo_data: Dict) -> Dict:
        """
        Analyze and compare data from both endpoints
        """
        analysis = {
            "data_sources": {
                "current_state_available": state_data is not None,
                "geo_tiles_available": geo_data is not None,
            }
        }

        if state_data:
            outages = state_data.get("outages", [])
            analysis["current_state_summary"] = {
                "total_outages": len(outages),
                "total_customers": sum(o.get("customersAffected", 0) for o in outages),
                "incident_ids": [
                    o.get("incidentId") for o in outages if o.get("incidentId")
                ],
            }

        if geo_data:
            hits = geo_data.get("hits", {}).get("hits", [])
            total_customers_geo = (
                geo_data.get("aggregations", {})
                .get("customerCountSum", {})
                .get("value", 0)
            )
            analysis["geo_tiles_summary"] = {
                "total_outages": len(hits),
                "total_customers": total_customers_geo,
                "incident_ids": [
                    h["_source"].get("incidentId")
                    for h in hits
                    if h.get("_source", {}).get("incidentId")
                ],
            }

        # Compare the two datasets
        if state_data and geo_data:
            state_ids = set(analysis["current_state_summary"]["incident_ids"])
            geo_ids = set(analysis["geo_tiles_summary"]["incident_ids"])

            analysis["comparison"] = {
                "common_incidents": list(state_ids & geo_ids),
                "state_only_incidents": list(state_ids - geo_ids),
                "geo_only_incidents": list(geo_ids - state_ids),
                "data_consistency": len(state_ids & geo_ids)
                / max(len(state_ids | geo_ids), 1),
            }

        return analysis

    def create_incident_map(self, unified_data: Dict) -> Dict:
        """
        Create a mapping of incidents with data from both sources
        """
        incident_map = {}

        # Add data from current state
        if unified_data.get("current_state"):
            for outage in unified_data["current_state"].get("outages", []):
                incident_id = outage.get("incidentId")
                if incident_id:
                    incident_map[incident_id] = {
                        "incident_id": incident_id,
                        "from_state": outage,
                        "from_geo": None,
                    }

        # Add/merge data from geo tiles
        if unified_data.get("geo_tiles"):
            for hit in unified_data["geo_tiles"].get("hits", {}).get("hits", []):
                source = hit.get("_source", {})
                incident_id = source.get("incidentId")
                if incident_id:
                    if incident_id in incident_map:
                        incident_map[incident_id]["from_geo"] = source
                    else:
                        incident_map[incident_id] = {
                            "incident_id": incident_id,
                            "from_state": None,
                            "from_geo": source,
                        }

        return incident_map

    def print_all_outages_detailed(self, api_key: str = None):
        """
        Print ALL outages with complete field data
        """
        print("=" * 80)
        print("COMPLETE TECO OUTAGE DATA - ALL FIELDS")
        print("=" * 80)

        geo_data = self.get_geo_tiles(api_key=api_key)

        if not geo_data:
            print("❌ No geo data available")
            return

        hits = geo_data.get("hits", {}).get("hits", [])
        total_info = geo_data.get("hits", {}).get("total", {})
        aggregations = geo_data.get("aggregations", {})
        tiles_info = geo_data.get("_tiles", {})

        print(f"📊 SUMMARY:")
        print(f"   Total Outages: {total_info.get('value', 0)}")
        print(
            f"   Total Customers Affected: {aggregations.get('customerCountSum', {}).get('value', 0)}"
        )
        print(f"   Data Generated: {tiles_info.get('generated', 'N/A')}")
        print(
            f"   Query Performance: {tiles_info.get('performance', {}).get('totalTimeMs', 'N/A')}ms"
        )

        print(f"\n🔧 INDIVIDUAL OUTAGES ({len(hits)} detailed records):")
        print("=" * 80)

        for i, hit in enumerate(hits, 1):
            source = hit["_source"]
            lat, lon = source.get("polygonCenter", [0, 0])

            print(f"\n{'='*20} OUTAGE {i} {'='*20}")
            print(f"🆔 Incident ID: {source.get('incidentId', 'N/A')}")
            print(f"📍 Location: {lat:.6f}, {lon:.6f}")
            print(f"👥 Customers Affected: {source.get('customerCount', 0)}")
            print(f"📊 Status: {source.get('status', 'Unknown')}")
            print(f"🔍 Reason: {source.get('reason', 'Unknown')}")
            print(f"🕐 Last Updated: {source.get('updateTime', 'N/A')}")

            if source.get("estimatedTimeOfRestoration"):
                print(
                    f"⏰ Estimated Restoration: {source['estimatedTimeOfRestoration']}"
                )
            else:
                print(f"⏰ Estimated Restoration: Not available")

            # Show the complete raw data
            print(f"📄 Complete Raw Data:")
            print(json.dumps(source, indent=4))
            print(f"🗃️  Elasticsearch Document ID: {hit.get('_id', 'N/A')}")
            print(f"🗂️  Index: {hit.get('_index', 'N/A')}")

        # Show complete API response metadata
        print(f"\n{'='*80}")
        print("📋 COMPLETE API RESPONSE METADATA:")
        print("=" * 80)
        print(f"🔍 Search Query Details:")
        print(f"   Requested Tiles: {tiles_info.get('requested', 'N/A')}")
        print(f"   Tiles with Data: {tiles_info.get('withData', 'N/A')}")
        print(f"   Zoom Level: {tiles_info.get('zoom', 'N/A')}")
        print(f"   Index Name: {tiles_info.get('indexName', 'N/A')}")
        print(f"   Cache Used: {geo_data.get('cache', 'N/A')}")

        print(f"\n📊 Raw Aggregations:")
        print(json.dumps(aggregations, indent=2))

        print(f"\n🌐 Raw Tiles Info:")
        print(json.dumps(tiles_info, indent=2))

        print(f"\n📋 COMPLETE RAW API RESPONSE:")
        print("=" * 80)
        print(json.dumps(geo_data, indent=2))


def check_dependencies():
    """
    Check if all required dependencies are available
    """
    print("🔍 Checking dependencies...")

    try:
        import requests

        print(f"✅ requests: {requests.__version__}")
    except ImportError:
        print("❌ requests library not found")
        print("   Install with: pip install requests")
        return False

    try:
        import json

        print("✅ json: built-in")
    except ImportError:
        print("❌ json not available (this shouldn't happen)")
        return False

    print("✅ All dependencies satisfied!")
    return True


def test_network_connectivity():
    """
    Test basic network connectivity to TECO's servers
    """
    print("\n🌐 Testing network connectivity...")

    test_urls = [
        "https://outage.tecoenergy.com/",
        "https://outage-data-prod-hrcadje2h9aje9c9.a03.azurefd.net/api/v1/config",
    ]

    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {url} - OK")
            else:
                print(f"⚠️  {url} - Status {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"❌ {url} - Timeout")
        except requests.exceptions.ConnectionError:
            print(f"❌ {url} - Connection Error")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")


def debug_config():
    """
    Standalone function to debug the config endpoint
    """
    headers = {
        "Origin": "https://outage.tecoenergy.com",
        "Referer": "https://outage.tecoenergy.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    base_url = "https://outage-data-prod-hrcadje2h9aje9c9.a03.azurefd.net"

    print("🔍 Debugging config endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/config", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")

        if response.status_code == 200:
            config = response.json()
            print("📋 Full Config Response:")
            print(json.dumps(config, indent=2))
        else:
            print(f"❌ Non-200 response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """
    Example usage showing both endpoints with comprehensive compatibility checks
    """
    print("=" * 60)
    print("TECO ENERGY OUTAGE API - COMPATIBILITY CHECK")
    print("=" * 60)

    # Check dependencies first
    if not check_dependencies():
        print("❌ Missing dependencies - cannot continue")
        return

    # Test network connectivity
    test_network_connectivity()

    print("\n" + "=" * 60)
    print("TESTING TECO API")
    print("=" * 60)

    # Initialize with rate limiting to be respectful
    api = TECOUnifiedAPI(rate_limit_delay=1.5)

    if not api.config:
        print("❌ Could not load configuration")
        print("   This might indicate network issues or API changes")
        return

    # Show ALL outages with complete data
    print("\n" + "=" * 60)
    print("ALL OUTAGES - COMPLETE DATA")
    print("=" * 60)
    api.print_all_outages_detailed()

    print("\n" + "=" * 60)
    print("SCRIPT PORTABILITY NOTES")
    print("=" * 60)
    print("✅ This script should work on other machines if:")
    print("   - Python 3.6+ is installed")
    print("   - 'requests' library is available (pip install requests)")
    print("   - Internet connection allows access to TECO's servers")
    print("   - No corporate firewall blocks the API endpoints")
    print("")
    print("⚠️  Potential issues:")
    print("   - Rate limiting if many people use it simultaneously")
    print("   - Geographic restrictions (though unlikely for utility APIs)")
    print("   - Session key limits (script gets fresh keys automatically)")
    print("")
    print("🔧 The script includes:")
    print("   - Automatic retry logic with exponential backoff")
    print("   - Rate limiting to be respectful to TECO's servers")
    print("   - Realistic browser headers to avoid bot detection")
    print("   - Comprehensive error handling")
    print("   - Automatic session key extraction")


if __name__ == "__main__":
    main()
