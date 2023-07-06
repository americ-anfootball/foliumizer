import geopandas as gpd
import json
import os
import tkinter as tk
from tkinter import Tk, filedialog

# create a global variable to store the mapping between aliases and file paths
file_path_mapping = {}

def import_data():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Shapefile", "*.shp"), ("GeoJSON", "*.geojson")])
    return file_path

def read_file(file_path):
    if file_path.endswith(".shp"):
        data = gpd.read_file(file_path)
        data = data.to_crs(epsg=4326)
        data.to_file(file_path[:-4] + ".geojson", driver="GeoJSON")
        return data
    elif file_path.endswith(".geojson"):
        data = gpd.read_file(file_path)
        data = data.to_crs(epsg=4326)
        return data

def open_file_dialog():
    root = Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(filetypes=[("Shapefiles", "*.shp"), ("GeoJSON files", "*.geojson")])
    result = []
    for i, file_path in enumerate(file_paths):
        if file_path.endswith(".shp"):
            gdf = gpd.read_file(file_path)
            geojson_path = file_path.replace(".shp", ".geojson")
            gdf.to_file(geojson_path, driver="GeoJSON")
            file_path = geojson_path
        gdf = gpd.read_file(file_path)
        gdf = gdf.to_crs("EPSG:4326")
        gdf.to_file(file_path, driver="GeoJSON")
        result.append(file_path)

    return result

def add_files(listbox):
    file_paths = open_file_dialog()
    for file_path in file_paths:
        # Use os.path.basename to get the filename without the path
        # Use os.path.splitext to split the filename and extension
        name, _ = os.path.splitext(os.path.basename(file_path))
        # store the mapping between the alias and the full file path
        file_path_mapping[name] = file_path
        listbox.insert(tk.END, name)

def on_select(listbox, property_listbox):
    selected_items = listbox.curselection()
    for item in selected_items:
        value = listbox.get(item)
        # look up the full file path based on the alias
        file_path = file_path_mapping[value]
        load_vector_data(file_path, property_listbox)

def load_vector_data(file_path, property_listbox):
    with open(file_path, "r") as f:
        geojson_data = json.load(f)

    property_names = set()
    for feature in geojson_data["features"]:
        property_names.update(feature["properties"].keys())

    property_listbox.delete(0, tk.END)
    for property_name in property_names:
        property_listbox.insert(tk.END, property_name)

def set_working_object_a(listbox, text_widget_a):
    selected_file_indices = listbox.curselection()
    if not selected_file_indices:
        message = "Please select a file"
        print(message)
        # delete the existing content of the text widget
        text_widget_a.delete("1.0", tk.END)
        # insert the new message into the text widget
        text_widget_a.insert(tk.END, message + "\n")
        return None

    selected_file_index = selected_file_indices[0]
    selected_file_alias = listbox.get(selected_file_index)
    # look up the full file path based on the alias
    selected_file = file_path_mapping[selected_file_alias]

    # Load the geojson data into a geopandas GeoDataFrame
    working_object_a = gpd.read_file(selected_file)
    # set the source_file attribute of the GeoDataFrame
    working_object_a.source_file = selected_file

    message = f"Working object geojson data set to {selected_file}"
    
    print(message)
    
    # delete the existing content of the text widget
    text_widget_a.delete("1.0", tk.END)
    # insert the new message into the text widget
    text_widget_a.insert(tk.END, message + "\n")

    return working_object_a

def set_working_object_b(property_listbox, text_widget_b):
    selected_property_indices = property_listbox.curselection()
    if not selected_property_indices:
        message = "Please select a property"
        print(message)
        # delete the existing content of the text widget
        text_widget_b.delete("1.0", tk.END)
        # insert the new message into the text widget
        text_widget_b.insert(tk.END, message + "\n")
        return None

    selected_property_index = selected_property_indices[0]
    selected_property = property_listbox.get(selected_property_index)

    # Set the working object b as the selected property
    working_object_b = selected_property

    message = f"Property of working object set to {selected_property}"
    
    # delete the existing content of the text widget
    text_widget_b.delete("1.0", tk.END)
    # insert the new message into the text widget
    text_widget_b.insert(tk.END, message + "\n")

    print(f"working_object_b: {working_object_b}")

    return working_object_b
