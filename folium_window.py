import branca
import folium
import geopandas as gpd
import json
import tkinter as tk
import webbrowser
from branca.element import MacroElement
from color_utils import get_styled_geojson
from folium import LayerControl
from folium_utils import calculate_bounding_box
from jinja2 import Template 
from tkinter import filedialog


class FoliumWindowLogic:
    def __init__(self, gui=None, working_object_a=None, working_object_b=None):
        self.gui = gui
        self.working_object_a = working_object_a
        self.working_object_b = working_object_b

    def get_all_styled_geojson(self):
        # Initialize a list to hold the styled GeoJSON data for each layer
        styled_geojson_list = []

        # Iterate over the layers in the Listbox
        for i, layer in enumerate(self.gui.folium_listbox.get(0, tk.END)):
            # Parse the layer string as a GeoJSON object
            geojson_data = json.loads(layer)

            # Style the GeoJSON data using the style information appended to the layer
            for feature in geojson_data['features']:
                feature['properties']['style'] = feature['properties'].get('style', {})

            # Add the styled GeoJSON data to the list
            styled_geojson_list.append(geojson_data)

        # Return the list of styled GeoJSON data
        return styled_geojson_list
        
    def get_property_names(self):
        # Get the first feature from the working_object_a GeoDataFrame
        feature = self.working_object_a.iloc[0]

        # Get the names of the properties from the feature
        property_names = list(feature.keys())

        return property_names

    def select_properties_for_popups(self):
        # Get the selected layer index from the Listbox widget
        selected_layer_indices = self.gui.folium_listbox.curselection()
        if not selected_layer_indices:
            message = "Please select a layer"
            print(message)
            return
        selected_layer_index = selected_layer_indices[0]

        # Open a new window to select properties for the popups of the selected layer
        LayerPropertiesWindow(self.gui, self.gui.master, self.layers[selected_layer_index])
 

class FoliumWindowGUI(tk.Toplevel):
    def __init__(self, master=None, logic=None):
        super().__init__(master)
        self.logic = logic
        self.logic.gui = self
        self.create_widgets()
        self.layer_count = 0
        self.top_layer = tk.StringVar()

    def create_widgets(self):
        # Create a frame to hold the Listbox and Scrollbars
        self.listbox_frame = tk.Frame(self)
        self.listbox_frame.pack()

        # Create the vertical scrollbar
        self.yscroll = tk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL)
        self.yscroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Create the horizontal scrollbar
        self.xscroll = tk.Scrollbar(self.listbox_frame, orient=tk.HORIZONTAL)
        self.xscroll.pack(side=tk.BOTTOM, fill=tk.X)

        # Create a Listbox widget to display the passed data
        self.folium_listbox = tk.Listbox(self.listbox_frame, selectmode=tk.SINGLE, exportselection=False, xscrollcommand=self.xscroll.set, yscrollcommand=self.yscroll.set)
        self.folium_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Attach the scrollbars to the Listbox
        self.yscroll.config(command=self.folium_listbox.yview)
        self.xscroll.config(command=self.folium_listbox.xview)
        
        # Create a label for the map title entry
        self.map_title_label = tk.Label(self, text="Map Title:")
        self.map_title_label.pack()

        # Create an Entry widget for the map title
        self.map_title_entry = tk.Entry(self, textvariable=self.map_title)
        self.map_title_entry.pack()
        
        # Create an OptionMenu widget for selecting the folium basemap layer
        basemap_options = ['stamen toner', 'stamen terrain', 'stamen watercolor', 'cartodb positron', 'cartodb dark matter', 'openstreetmap', 'none']
        self.basemap_var = tk.StringVar(self)
        self.basemap_var.set(basemap_options[0])
        self.basemap_option_menu = tk.OptionMenu(self, self.basemap_var, *basemap_options)
        self.basemap_option_menu.pack()

        # Create a button to create the folium map from active layers
        self.create_map_button = tk.Button(self, text="Create Folium Map from Active Layers", command=self.create_map)
        self.create_map_button.pack()

    def add_layer(self, geojson_str):
        # Increment the layer count
        self.layer_count += 1

        # Insert the alias into the folium listbox
        alias = f"Layer {self.layer_count}"
        self.folium_listbox.insert(tk.END, alias)

        # Update or create the top layer menu and label
        if hasattr(self, 'top_layer_menu'):
            menu = self.top_layer_menu["menu"]
            menu.add_command(label=alias, command=lambda value=alias: self.top_layer.set(value))
            menu.invoke(0)  # Set the top layer to the first item in the menu
            self.top_layer_menu.pack()
            self.top_layer_label.pack()
        else:
            first_value = alias
            self.top_layer_label = tk.Label(self, text="Top Layer:")
            self.top_layer_label.pack()
            self.top_layer_menu = tk.OptionMenu(self, self.top_layer, first_value)
            self.top_layer_menu.pack()

    def create_map(self):
        # Get the map title from the Entry widget
        title = self.map_title.get()
        
        # Add a title to the map
        title = self.gui.title_entry.get()
        if title:
            title_html = f"""
            <div id="map-title" style="position: fixed; bottom: 50px; left: 50px; height: 40px; border:2px solid grey; z-index:9999; font-size:20px; background-color: white;">  {title}
            </div>
            <script>
                // Get the map title element
                var mapTitle = document.getElementById('map-title');
                
                // Measure the width of the title text
                var canvas = document.createElement('canvas');
                var context = canvas.getContext('2d');
                context.font = '20px sans-serif';
                var metrics = context.measureText(mapTitle.textContent);
                
                // Set the width of the map title element
                mapTitle.style.width = (metrics.width + 20) + 'px';
            </script>
            """
            m.get_root().html.add_child(folium.Element(title_html))

        # Get the selected top layer from the OptionMenu
        top_layer = self.top_layer.get()

        # Get the list of active layers from the Listbox
        active_layers = list(self.folium_listbox.get(0, tk.END))

        # Get the selected folium basemap layer from the OptionMenu widget
        basemap_layer = self.basemap_var.get()

        # Create a new folium map with the selected basemap layer
        if basemap_layer == 'none':
            m = folium.Map()
        else:
            m = folium.Map(tiles=basemap_layer)

        # Get the value of the top layer
        top_layer_value = self.top_layer.get()

        # Calculate the bounding box of the GeoJSON data
        min_lng, min_lat, max_lng, max_lat = float('inf'), float('inf'), float('-inf'), float('-inf')

        # Define a style function
        def style_function(feature):
            return feature['properties'].get('style', {})

        # Iterate over the layers in the Listbox
        for i, layer in enumerate(self.folium_listbox.get(0, tk.END)):
            # Parse the layer string as a GeoJSON object
            geojson_data = json.loads(layer)

            # Update the bounding box with the coordinates from this layer
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

            # Check if this is the top layer
            if layer == top_layer_value:
                # Add this layer to the map with show=True and the style function
                folium.GeoJson(geojson_data, style_function=style_function, overlay=True, show=True).add_to(m)
            else:
                # Add this layer to the map with show=False and the style function
                folium.GeoJson(geojson_data, style_function=style_function, overlay=True, show=False).add_to(m)

        # Calculate the centroid of the bounding box
        centroid_lng=(min_lng+max_lng)/2
        centroid_lat=(min_lat+max_lat)/2

        # Center the folium map at the centroid of the bounding box
        m.location=[centroid_lat,centroid_lng]

        # Fit the map view to the bounding box of the GeoJSON data
        m.fit_bounds([[min_lat,min_lng],[max_lat,max_lng]])

        # Add a layer control to the map
        if self.gui.layer_control_var.get():
            LayerControl().add_to(m)
            
        # Display a file dialog window to select a file name and location for saving the folium map
        file_name = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Files", "*.html")])

        # Save the folium map to the selected file
        m.save(file_name)

        # Open the folium map in a web browser
        webbrowser.open(file_name)

        # Return the folium map object
        return m
