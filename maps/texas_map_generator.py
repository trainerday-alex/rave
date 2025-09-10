#!/usr/bin/env python3

import random
import requests
import urllib.parse
from typing import List, Tuple

MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoidHJhaW5lcmRheSIsImEiOiJjbHd4Zmkzc3cxODM4Mm9yMXM5cm85MTQxIn0.wrlMU1uS94Ml2oDZHc3VXA"

import math

# San Antonio coordinates
SAN_ANTONIO_LAT = 29.4241
SAN_ANTONIO_LON = -98.4936

def generate_coordinates_around_san_antonio(num_points: int = 1000, radius_miles: int = 100) -> List[Tuple[float, float]]:
    """Generate random coordinates within a radius of San Antonio."""
    coordinates = []
    # Convert miles to degrees (approximately 1 mile = 0.0145 degrees)
    radius_degrees = radius_miles * 0.0145
    
    for _ in range(num_points):
        # Generate random angle and distance
        angle = random.uniform(0, 2 * math.pi)
        # Use sqrt to get uniform distribution in circular area
        distance = radius_degrees * math.sqrt(random.uniform(0, 1))
        
        # Calculate coordinates
        lat = SAN_ANTONIO_LAT + distance * math.cos(angle)
        lon = SAN_ANTONIO_LON + distance * math.sin(angle)
        
        coordinates.append((lon, lat))
    return coordinates

def create_mapbox_url(coordinates: List[Tuple[float, float]], 
                     width: int = 1024, 
                     height: int = 1024) -> str:
    """Create Mapbox Static Image API URL with overlays."""
    
    base_url = "https://api.mapbox.com/styles/v1/mapbox/streets-v11/static"
    
    # Use only first 100 points to avoid URL length limit
    limited_coords = coordinates[:100]
    overlays = []
    for lon, lat in limited_coords:
        overlays.append(f"pin-s+ff0000({lon:.4f},{lat:.4f})")
    
    overlay_string = ",".join(overlays)
    
    # Center on Texas but show whole state
    texas_center_lon = -99.9018
    texas_center_lat = 31.9686
    
    url = f"{base_url}/{overlay_string}/{texas_center_lon},{texas_center_lat},6/{width}x{height}@2x"
    url += f"?access_token={MAPBOX_ACCESS_TOKEN}"
    
    return url

def download_map_image(url: str, filename: str = "texas_map_with_dots.png") -> bool:
    """Download map image from Mapbox API."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        print(f"Map image saved as {filename}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return False

def main():
    """Generate map with 1000 dots within 100 miles of San Antonio."""
    print("Generating 1000 random coordinates within 100 miles of San Antonio...")
    coordinates = generate_coordinates_around_san_antonio(1000, 100)
    
    print("Building Mapbox Static Image API URL (using first 100 points due to URL length limits)...")
    map_url = create_mapbox_url(coordinates)
    
    print("Downloading map image...")
    success = download_map_image(map_url, "maps/san_antonio_area_map.png")
    
    if success:
        print("San Antonio area map with clustered dots generated successfully!")
        print(f"Note: Displayed 100 out of 1000 generated points due to API URL length limitations.")
    else:
        print("Failed to generate map image.")

if __name__ == "__main__":
    main()