#!/usr/bin/env python3

import random
import requests
import math
import numpy as np
from PIL import Image, ImageDraw
from typing import List, Tuple, Dict
from dataclasses import dataclass

MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoidHJhaW5lcmRheSIsImEiOiJjbHd4Zmkzc3cxODM4Mm9yMXM5cm85MTQxIn0.wrlMU1uS94Ml2oDZHc3VXA"

# San Antonio coordinates
SAN_ANTONIO_LAT = 29.4241
SAN_ANTONIO_LON = -98.4936

# Texas map bounds for coordinate conversion
TEXAS_BOUNDS = {
    "min_lat": 25.837377,
    "max_lat": 36.500704,
    "min_lon": -106.645646,
    "max_lon": -93.508292
}

@dataclass
class Cluster:
    center_lat: float
    center_lon: float
    point_count: int
    points: List[Tuple[float, float]]

def generate_coordinates_around_san_antonio(num_points: int = 2000, radius_miles: int = 100) -> List[Tuple[float, float]]:
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
        
        coordinates.append((lat, lon))
    return coordinates

def create_clusters(points: List[Tuple[float, float]], max_clusters: int = 50, cluster_radius: float = 0.1) -> List[Cluster]:
    """Create clusters from points using a more aggressive clustering algorithm."""
    clusters = []
    remaining_points = points.copy()
    
    # Sort points by density (points with more nearby neighbors first)
    point_densities = []
    for i, point in enumerate(remaining_points):
        nearby_count = sum(1 for other_point in remaining_points 
                          if math.sqrt((point[0] - other_point[0])**2 + (point[1] - other_point[1])**2) <= cluster_radius)
        point_densities.append((nearby_count, i, point))
    
    # Sort by density (highest first)
    point_densities.sort(reverse=True, key=lambda x: x[0])
    remaining_points = [x[2] for x in point_densities]
    
    while remaining_points and len(clusters) < max_clusters:
        # Take first point (highest density) as cluster center
        center_point = remaining_points.pop(0)
        cluster_points = [center_point]
        
        # Find all points within cluster radius
        points_to_remove = []
        for i, point in enumerate(remaining_points):
            distance = math.sqrt((point[0] - center_point[0])**2 + (point[1] - center_point[1])**2)
            if distance <= cluster_radius:
                cluster_points.append(point)
                points_to_remove.append(i)
        
        # Remove clustered points from remaining points (reverse order to maintain indices)
        for i in reversed(points_to_remove):
            remaining_points.pop(i)
        
        # Create cluster
        center_lat = sum(p[0] for p in cluster_points) / len(cluster_points)
        center_lon = sum(p[1] for p in cluster_points) / len(cluster_points)
        
        cluster = Cluster(
            center_lat=center_lat,
            center_lon=center_lon,
            point_count=len(cluster_points),
            points=cluster_points
        )
        clusters.append(cluster)
    
    return clusters

def get_base_map_url(width: int = 1280, height: int = 1280) -> str:
    """Get base map URL without any overlays."""
    base_url = "https://api.mapbox.com/styles/v1/mapbox/streets-v11/static"
    
    # Center on Texas
    texas_center_lon = -99.9018
    texas_center_lat = 31.9686
    
    url = f"{base_url}/{texas_center_lon},{texas_center_lat},6/{width}x{height}@2x"
    url += f"?access_token={MAPBOX_ACCESS_TOKEN}"
    
    return url

def lat_lon_to_pixel(lat: float, lon: float, image_width: int, image_height: int) -> Tuple[int, int]:
    """Convert latitude/longitude to pixel coordinates on the Texas map."""
    # Normalize coordinates to 0-1 range based on Texas bounds
    lon_norm = (lon - TEXAS_BOUNDS["min_lon"]) / (TEXAS_BOUNDS["max_lon"] - TEXAS_BOUNDS["min_lon"])
    lat_norm = (TEXAS_BOUNDS["max_lat"] - lat) / (TEXAS_BOUNDS["max_lat"] - TEXAS_BOUNDS["min_lat"])
    
    # Convert to pixel coordinates with some padding
    padding = 0.1  # 10% padding
    x = int((lon_norm * (1 - 2 * padding) + padding) * image_width)
    y = int((lat_norm * (1 - 2 * padding) + padding) * image_height)
    
    return x, y

def draw_clusters_on_image(image_path: str, clusters: List[Cluster], output_path: str):
    """Draw clusters on the map image with varying dot sizes."""
    # Open the base map image
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    # Define colors for different cluster sizes
    colors = {
        'small': (255, 100, 100),    # Light red for 1-5 points
        'medium': (255, 50, 50),     # Medium red for 6-20 points
        'large': (200, 0, 0),        # Dark red for 21+ points
    }
    
    # Sort clusters by size to draw larger ones first (so they appear behind smaller ones)
    sorted_clusters = sorted(clusters, key=lambda c: c.point_count, reverse=True)
    
    for cluster in sorted_clusters:
        x, y = lat_lon_to_pixel(cluster.center_lat, cluster.center_lon, img.width, img.height)
        
        # Determine dot size and color based on cluster size - keep original sizes
        if cluster.point_count == 1:
            radius = 4
            color = colors['small']
        elif cluster.point_count <= 10:
            radius = 8
            color = colors['small']
        elif cluster.point_count <= 50:
            radius = 16
            color = colors['medium']
        elif cluster.point_count <= 100:
            radius = 24
            color = colors['large']
        else:
            radius = 32
            color = (150, 0, 0)  # Even darker red for very large clusters
        
        # Draw circle without border
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
        
        # Add text for clusters with more than 1 point
        if cluster.point_count > 1:
            text = str(cluster.point_count)
            
            # Adjust font size based on dot size - smaller dots get smaller font
            if radius <= 8:  # Small dots
                font_size = 14  # 30% smaller than 20
            else:  # Medium and large dots
                font_size = 20
            
            # Try to load a font, fall back to default if not available
            try:
                from PIL import ImageFont
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
            except:
                font = None
            
            # Draw text centered using anchor parameter
            if font:
                draw.text((x, y), text, fill=(255, 255, 255), font=font, anchor="mm")
            else:
                # Fallback for default font - manual centering
                if radius <= 8:
                    text_width = len(text) * 8
                    text_height = 12
                else:
                    text_width = len(text) * 12
                    text_height = 16
                text_x = x - text_width // 2
                text_y = y - text_height // 2
                draw.text((text_x, text_y), text, fill=(255, 255, 255))
    
    # Save the final image
    img.save(output_path)
    print(f"Clustered map saved as {output_path}")

def main():
    """Generate clustered map with 2000 points around San Antonio."""
    print("Generating 2000 random coordinates within 100 miles of San Antonio...")
    coordinates = generate_coordinates_around_san_antonio(2000, 100)
    
    print("Creating clusters from points...")
    clusters = create_clusters(coordinates, max_clusters=50)
    print(f"Created {len(clusters)} clusters from 2000 points")
    
    print("Downloading base map image...")
    base_map_url = get_base_map_url()
    response = requests.get(base_map_url)
    response.raise_for_status()
    
    base_map_path = "maps/texas_base_map.png"
    with open(base_map_path, 'wb') as f:
        f.write(response.content)
    print(f"Base map saved as {base_map_path}")
    
    print("Drawing clusters on map...")
    output_path = "maps/texas_clustered_map_hires.png"
    draw_clusters_on_image(base_map_path, clusters, output_path)
    
    print("Clustered map generation complete!")
    print(f"Total points: 2000")
    print(f"Clusters shown: {len(clusters)}")

if __name__ == "__main__":
    main()