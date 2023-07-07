import geopandas as gpd
import tkinter as tk

def calculate_bounding_box(geojson_data):
    # Initialize the bounding box values
    min_lng, min_lat, max_lng, max_lat = float('inf'), float('inf'), float('-inf'), float('-inf')

    # Iterate over the features in the GeoJSON data
    for feature in geojson_data['features']:
        coords = feature['geometry']['coordinates']
        if feature['geometry']['type'] == 'Point':
            lng, lat = coords
            min_lng, max_lng = min(min_lng, lng), max(max_lng, lng)
            min_lat, max_lat = min(min_lat, lat), max(max_lat, lat)
        elif feature['geometry']['type'] in ['LineString', 'MultiPoint']:
            for point in coords:
                lng, lat = point
                min_lng, max_lng = min(min_lng, lng), max(max_lng, lng)
                min_lat, max_lat = min(min_lat,lat),max(max_lat,lat)
        elif feature['geometry']['type'] in ['Polygon', 'MultiLineString']:
            for ring in coords:
                for point in ring:
                    lng,lat=point
                    min_lng,max_lng=min(min_lng,lng),max(max_lng,lng)
                    min_lat,max_lat=min(min_lat,lat),max(max_lat,lat)
        elif feature['geometry']['type']=='MultiPolygon':
            for polygon in coords:
                for ring in polygon:
                    for point in ring:
                        lng,lat=point
                        min_lng,max_lng=min(min_lng,lng),max(max_lng,lng)
                        min_lat,max_lat=min(min_lat,lat),max(max_lat,lat)

    # Return the bounding box values
    return (min_lng, min_lat, max_lng, max_lat)

def style_function(feature):
    return feature['properties'].get('style', {})
