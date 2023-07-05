import colorsys
import geopandas as gpd
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import tkinter as tk
from matplotlib.colors import ListedColormap
from scipy.stats.mstats import mquantiles

def generate_color_ramp(hue1, hue2, bins, ramp_type):
    color_ramp = []
    step = 50 / (bins - 1)
    for i in range(bins):
        if ramp_type == 'diverging':
            if bins % 2 == 1 and i == bins // 2:
                hue = 0
                saturation = 0
                brightness = 100
            else:
                hue = hue1 if i < bins / 2 else hue2
                if i < bins / 2:
                    saturation = 75 - i * step
                    brightness = 25 + i * step
                else:
                    saturation = 25 + i * step
                    brightness = 75 - i * step
        else:
            hue = hue1
            saturation = 25 + i * step
            brightness = 75 - i * step
        color_ramp.append((hue, saturation, brightness))
    return color_ramp

def hsb_to_rgb(h, s, b):
    s /= 100
    b /= 100
    r_out, g_out, b_out = colorsys.hsv_to_rgb(h/360, s, b)
    return r_out, g_out, b_out

def generate_and_display_color_palette(canvas, apply_button, hue1, hue2, bins, ramp_type):
    color_ramp = generate_color_ramp(hue1, hue2, bins, ramp_type)

    canvas.delete('all')

    width = canvas.winfo_width() / len(color_ramp)
    for i, (h, s, b) in enumerate(color_ramp):
        x0 = i * width
        y0 = 0
        x1 = (i + 1) * width
        y1 = canvas.winfo_height()
        r, g, b = hsb_to_rgb(h, s, b)
        fill_color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
        canvas.create_rectangle(x0, y0, x1, y1, fill=fill_color)

    return color_ramp

def set_color_ramp(color_ramp_listbox, text_widget_c):
    selected_color_ramp_indices = color_ramp_listbox.curselection()
    if not selected_color_ramp_indices:
        message = "Please select a color ramp"
        print(message)

        text_widget_c.insert(tk.END, message + "\n")
        return None

    selected_color_ramp_index = selected_color_ramp_indices[0]
    selected_color_ramp = color_ramp_listbox.get(selected_color_ramp_index)

    message = f"Color ramp set to {selected_color_ramp}"

    text_widget_c.insert(tk.END, message + "\n")

    return selected_color_ramp

def get_styled_geojson(geojson_data, selected_property, classification_method, bins, color_ramp):
    print(f"color_ramp: {color_ramp}")
    if not geojson_data.empty:
        # Convert the GeoJSON data to a GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(geojson_data)
    
    # Classify the data into bins
    if selected_property:
        # Choose a classification method
        if classification_method == 'quantiles':
            bin_edges = mquantiles(gdf[selected_property], prob=np.linspace(0, 1, bins + 1))
        elif classification_method == 'equal_interval':
            bin_edges = np.linspace(gdf[selected_property].min(), gdf[selected_property].max(), bins + 1)
        elif classification_method == 'standard_deviation':
            p = [100 / bins * i for i in range(bins + 1)]
            bin_edges = np.percentile(gdf[selected_property], p)
        else:
            raise ValueError(f"Invalid classification method: {classification_method}")

        gdf['bin'] = pd.cut(gdf[selected_property], bins=bin_edges, labels=False, include_lowest=True)
        
        # Add an extra bin edge that is smaller than the minimum value of the data
        min_value = gdf[selected_property].min()
        bin_edges = [min_value - 1] + list(bin_edges)
        
        # Add an extra bin edge that is larger than the maximum value of the data
        max_value = gdf[selected_property].max()
        bin_edges = list(bin_edges) + [max_value + 1]
        
        # Assign each feature to a bin
        gdf['bin'] = pd.cut(gdf[selected_property], bins=bin_edges, labels=False, include_lowest=True)
    
    # Create a custom colormap from the selected color ramp
    if color_ramp:
        colors = [hsb_to_rgb(h, s, b) for h, s, b in color_ramp]
        cmap = ListedColormap(colors)
    else:
        cmap = None
    
    # Convert the GeoDataFrame to a GeoJSON string
    geojson_str = gdf.to_json()
    
    # Apply the colormap to the features in the GeoJSON string
    if cmap:
        geojson_data = json.loads(geojson_str)
        for feature in geojson_data['features']:
            try:
                feature['properties']['style'] = {
                    'fillColor': cmap(feature['properties']['bin']),
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7,
                }
            except KeyError:
                print("KeyError: 'bin' not found")
                # Handle the error here
                pass
        geojson_str = json.dumps(geojson_data)
    
        return geojson_str
    else:
        return None

def generate_styled_geojson(color_ramp, bins, classification_method, working_object_a, working_object_b):
    # Generate and display a styled GeoJSON object
    geojson_str = get_styled_geojson(working_object_a, working_object_b, classification_method, bins, color_ramp)
    if geojson_str:
        # Convert the GeoJSON string to a GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(json.loads(geojson_str))

        # Create a colormap from the selected color ramp
        if color_ramp:
            colors = [hsb_to_rgb(h, s, b) for h, s, b in color_ramp]
            cmap = ListedColormap(colors)
        else:
            cmap = None

        # Plot the GeoDataFrame using the custom colormap
        print("Plotting GeoDataFrame")
        if cmap:
            gdf.plot(column='bin', cmap=cmap)
            
            plt.show()
            
        else:
            gdf.plot()
            
            gdf.plot()
            
        print("GeoDataFrame plotted")
            
