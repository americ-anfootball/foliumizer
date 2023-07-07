import ezdxf
import geopandas as gpd
import json
import os
import osmnx as ox
import pandas as pd
import sqlite3
import tkinter as tk
from requests import Request
from shapely.geometry import Point, LineString
from sqlalchemy import create_engine
import tiledb
from tkinter import Tk, filedialog

# create a global variable to store the mapping between aliases and file paths
file_path_mapping = {}

def import_data():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("All supported files", "*.*"), ("Shapefile", "*.shp"), ("GeoJSON", "*.geojson"), ("CSV", "*.csv"), ("GDB", "*.gdb"), ("DXF", "*.dxf"), ("GML", "*.gml"), ("GPKG", "*.gpkg"), ("KML", "*.kml"), ("OSM", "*.osm"), ("SQLite", "*.sqlite"), ("TileDB", "*.tdb"), ("Excel files", "*.xls;*.xlsx")])
    return file_path

def read_file(file_path, x_col=None, y_col=None, crs=None):
    if file_path.endswith(".shp"):
        data = gpd.read_file(file_path)
        data = data.to_crs(epsg=4326)
        data.to_file(file_path[:-4] + ".geojson", driver="GeoJSON")
        return data
    elif file_path.endswith(".geojson") or file_path.endswith(".json") or file_path.endswith(".topojson"):
        data = gpd.read_file(file_path)
        data = data.to_crs(epsg=4326)
        return data
    elif file_path.endswith(".csv"):
        data = gpd.read_file(file_path)
        return data
    elif file_path.endswith(".gdb"):
        layers = fiona.listlayers(file_path)
        data = gpd.read_file(file_path, layer=layers[0])
        return data
    elif file_path.endswith(".dxf"):
        # Read the DXF file
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()

        # Extract points and lines from the DXF file
        points = []
        lines = []
        for entity in msp:
            if entity.dxftype() == 'POINT':
                points.append(Point(entity.dxf.location))
            elif entity.dxftype() == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
                lines.append(LineString([start, end]))

        # Create a GeoDataFrame from the extracted data
        data = gpd.GeoDataFrame(geometry=points + lines)
        return data
    elif file_path.endswith(".gml"):
        data = gpd.read_file(file_path)
        return data
    elif file_path.endswith(".gpkg"):
        layers = fiona.listlayers(file_path)
        data = gpd.read_file(file_path, layer=layers[0])
        return data
    elif file_path.endswith(".kml"):
        data = gpd.read_file(file_path, driver='KML')
        return data
    elif file_path.endswith(".osm"):
        # Read the OSM file
        graph = ox.graph_from_xml(file_path)
        nodes, edges = ox.graph_to_gdfs(graph)

        # Create a GeoDataFrame from the extracted data
        data = gpd.GeoDataFrame(geometry=nodes.geometry)
        return data
    elif file_path.endswith(".sqlite"):
         # Connect to the SQLite database
         conn = sqlite3.connect(file_path)
         cursor = conn.cursor()

         # Execute a query to get the data from the database
         cursor.execute("SELECT * FROM my_table")
         data = cursor.fetchall()

         # Create a DataFrame from the extracted data
         df = pd.DataFrame(data, columns=[col[0] for col in cursor.description])

         # Convert the DataFrame into a GeoDataFrame
         gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

         return gdf
    elif file_path.endswith(".tdb"):
         # Open the TileDB array for reading
         with tiledb.open(file_path, mode='r') as arr:
             # Query the data from the array
             data = arr[:]

         # Create a DataFrame from the extracted data
         df = pd.DataFrame(data)

         # Convert the DataFrame into a GeoDataFrame
         gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

         return gdf
    elif file_path.endswith(".xls") or file_path.endswith(".xlsx"):
         # Read the Excel file
         df = pd.read_excel(file_path)

         # Convert the DataFrame into a GeoDataFrame
         gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[x_col], df[y_col]), crs=crs)

         return gdf

def open_file_dialog():
    root = Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(filetypes=[("All supported files", "*.*"), ("Shapefiles", "*.shp"), ("GeoJSON files", "*.geojson"), ("CSV files", "*.csv"), ("GDB files", "*.gdb"), ("DXF files", "*.dxf"), ("GML files", "*.gml"), ("GPKG files", "*.gpkg"), ("KML files", "*.kml"), ("OSM files", "*.osm"), ("SQLite files", "*.sqlite"), ("TileDB files", "*.tdb"), ("Excel files", "*.xls;*.xlsx")])
    result = []
    for i, file_path in enumerate(file_paths):
        if file_path.endswith(".shp"):
            gdf = gpd.read_file(file_path)
            geojson_path = file_path.replace(".shp", ".geojson")
            gdf.to_file(geojson_path, driver="GeoJSON")
            file_path = geojson_path
        elif file_path.endswith(".xls") or file_path.endswith(".xlsx"):
            # Read the Excel file
            df = pd.read_excel(file_path)

            # Convert the DataFrame into a GeoDataFrame
            # You will need to specify the columns in the DataFrame that contain the x and y coordinates of the geometry data
            x_col = 'longitude'
            y_col = 'latitude'
            gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[x_col], df[y_col]))

            # Save the GeoDataFrame as a GeoJSON file
            geojson_path = file_path.replace(".xls", ".geojson").replace(".xlsx", ".geojson")
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
        for property_name, property_value in feature["properties"].items():
            # Check if the property value is a valid data type
            if isinstance(property_value, (str, int, float, bool, list, dict)):
                property_names.add(property_name)

    # Sort the property names in alphabetical order
    property_names = sorted(property_names)

    property_listbox.delete(0, tk.END)
    for property_name in property_names:
        property_listbox.insert(tk.END, property_name)

def read_dxf(file_path):
    # Read the DXF file
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    # Extract points and lines from the DXF file
    points = []
    lines = []
    for entity in msp:
        if entity.dxftype() == 'POINT':
            points.append(Point(entity.dxf.location))
        elif entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            lines.append(LineString([start, end]))

    # Create a GeoDataFrame from the extracted data
    data = gpd.GeoDataFrame(geometry=points + lines)
    return data

def read_osm(file_path):
    # Read the OSM file
    graph = ox.graph_from_xml(file_path)
    nodes, edges = ox.graph_to_gdfs(graph)

    # Create a GeoDataFrame from the extracted data
    data = gpd.GeoDataFrame(geometry=nodes.geometry)
    return data

def read_sqlite(file_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()

    # Execute a query to get the data from the database
    cursor.execute("SELECT * FROM my_table")
    data = cursor.fetchall()

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(data, columns=[col[0] for col in cursor.description])

    # Convert the DataFrame into a GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

    return gdf

def read_postgis_dump(dump_file, table_name, geom_col, crs=None):
    # Restore the dump into a PostgreSQL database
    # This step assumes that you have already created a PostgreSQL database
    # and have the necessary permissions to restore data into it
    db_name = "my_database"
    db_user = "my_user"
    db_password = "my_password"
    db_host = "localhost"
    db_port = 5432
    restore_command = f"pg_restore -d {db_name} -U {db_user} -h {db_host} -p {db_port} {dump_file}"
    os.system(restore_command)

    # Create a SQLAlchemy engine to connect to the database
    engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

    # Read data from the specified table into a GeoDataFrame
    sql = f"SELECT * FROM {table_name}"
    gdf = gpd.read_postgis(sql, engine, geom_col=geom_col, crs=crs)

    return gdf
    
def read_tiledb(uri):
    # Open the TileDB array for reading
    with tiledb.open(uri, mode='r') as arr:
        # Query the data from the array
        data = arr[:]

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(data)

    # Convert the DataFrame into a GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

    return gdf
    
def read_topojson(file_path):
    # Read the TopoJSON file
    data = gpd.read_file(file_path)
    return data
    
def read_wfs(wfs_url, layer_name):
    # Specify the parameters for fetching the data
    params = dict(service='WFS', version="2.0.0", request='GetFeature', typeName=layer_name, outputFormat='json')

    # Parse the URL with parameters
    wfs_request_url = Request('GET', wfs_url, params=params).prepare().url

    # Read data from URL
    data = gpd.read_file(wfs_request_url)
    return data

def read_excel(file_path, x_col, y_col, crs=None):
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Convert the DataFrame into a GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[x_col], df[y_col]), crs=crs)

    return gdf

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
