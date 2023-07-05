# folium_window.py

import tkinter as tk
from tkinter import filedialog
import webbrowser
import json
import folium
from folium.features import GeoJsonPopup
from folium import LayerControl
from branca.element import MacroElement
from jinja2 import Template 

class FoliumWindow(tk.Toplevel):

    def update_layers_listbox(self):
        # Clear the layers_listbox
        self.layers_listbox.delete(0, tk.END)
        print("Updating layers_listbox with layers:", self.layers)

        # Add the layers to the layers_listbox
        for layer in self.layers:
            self.layers_listbox.insert(tk.END, layer)
        
    def update_layer_visibility(self):
        # Get the indices of the selected items in the visible_layers_listbox
        selected_indices = self.visible_layers_listbox.curselection()

        # Update the visibility of the layers
        for i, layer in enumerate(self.layers):
            if i in selected_indices:
                layer["show"] = True
            else:
                layer["show"] = False

    def add_layer(self, layer):
        # Add the layer to the list of layers
        self.layers.append({"data": layer, "show": True, "overlay": True})
        print("Received data from color_window pane:", layer)

        # Update the layers_listbox and visible_layers_listbox
        self.update_layers_listbox()
        self.update_visible_layers_listbox()

    def __init__(self, master, main_window, working_object_a, working_object_b):
        super().__init__(master)
        self.title('Folium Map')
        self.main_window = main_window
        self.working_object_a = working_object_a
        self.working_object_b = working_object_b
        self.layers = []
        self.create_widgets()
        
    def create_widgets(self):
        # Create a Listbox widget for selecting the layers
        self.layers_listbox_label = tk.Label(self, text="Layers:")
        self.layers_listbox_label.pack()
        self.layers_listbox = tk.Listbox(self)
        self.layers_listbox.pack()
        
        # Create a Button widget for opening a new window to select properties for the popups of the selected layer
        self.select_properties_button = tk.Button(self, text="Select Properties for Popups", command=self.select_properties_for_popups)
        self.select_properties_button.pack()
        
        # Create a Listbox widget for selecting the visible layers
        self.visible_layers_listbox_label = tk.Label(self, text="Select Top Layer:")
        self.visible_layers_listbox_label.pack()
        self.visible_layers_listbox = tk.Listbox(self, selectmode=tk.MULTIPLE)
        self.visible_layers_listbox.pack()
        
        # Create a Button widget for updating the visibility of the layers
        self.update_visibility_button = tk.Button(self, text="Update Layer Visibility", command=self.update_layer_visibility)
        self.update_visibility_button.pack()
        
        # Create an OptionMenu widget for selecting the folium basemap layer
        basemap_options = ['stamen toner', 'stamen terrain', 'stamen watercolor', 'cartodb positron', 'cartodb dark matter', 'openstreetmap', 'none']
        self.basemap_var = tk.StringVar(self)
        self.basemap_var.set(basemap_options[0])
        self.basemap_option_menu = tk.OptionMenu(self, self.basemap_var, *basemap_options)
        self.basemap_option_menu.pack()
        
        # Create a Label widget to display instructions
        self.instructions_label = tk.Label(self, text="Select properties to include in popups:")
        self.instructions_label.pack()
        
        # Create Checkbutton widgets for selecting properties to include in popups
        self.property_vars = {}
        for property_name in self.get_property_names():
            var = tk.BooleanVar(self)
            checkbutton = tk.Checkbutton(self, text=property_name, variable=var)
            checkbutton.pack()
            self.property_vars[property_name] = var
            
        # Create an Entry widget for entering the map title
        self.title_label = tk.Label(self, text="Map Title:")
        self.title_label.pack()
        self.title_entry = tk.Entry(self)
        self.title_entry.pack()
        
        # Create a Checkbutton widget for enabling the layer control
        self.layer_control_var = tk.BooleanVar(self)
        self.layer_control_checkbutton = tk.Checkbutton(self, text="Enable Layer Control", variable=self.layer_control_var)
        self.layer_control_checkbutton.pack()
        
        # Create an Entry widget for entering the name of the GeoJSON layer
        self.geojson_layer_label = tk.Label(self, text="GeoJSON Layer Name:")
        self.geojson_layer_label.pack()
        self.geojson_layer_entry = tk.Entry(self)
        self.geojson_layer_entry.pack()
        
        # Create a Button widget to generate the folium map
        self.generate_button = tk.Button(self, text="Generate Folium Map", command=self.generate_folium_map)
        self.generate_button.pack()
    
    def get_property_names(self):
        # Get the first feature from the working_object_a GeoDataFrame
        feature = self.working_object_a.iloc[0]

        # Get the names of the properties from the feature
        property_names = list(feature.keys())

        return property_names
        
    def select_properties_for_popups(self):
        # Get the selected layer index from the Listbox widget
        selected_layer_indices = self.layers_listbox.curselection()
        if not selected_layer_indices:
            message = "Please select a layer"
            print(message)
            return
        selected_layer_index = selected_layer_indices[0]
        
        # Open a new window to select properties for the popups of the selected layer
        LayerPropertiesWindow(self, self.main_window, self.layers[selected_layer_index])
    
    def generate_folium_map(self):
        try:
            # Get the selected GeoJSON data object
            geojson_data = self.working_object_a
            
            # Get the selected folium basemap layer from the OptionMenu widget
            basemap_layer = self.basemap_var.get()
            
            # Create a new folium map with the selected basemap layer
            if basemap_layer == 'none':
                m = folium.Map()
            else:
                m = folium.Map(tiles=basemap_layer)
            
            # Calculate the bounding box of the GeoJSON data
            min_lng, min_lat, max_lng, max_lat = float('inf'), float('inf'), float('-inf'), float('-inf')
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

			# Calculate the centroid of the bounding box
            centroid_lng=(min_lng+max_lng)/2
            centroid_lat=(min_lat+max_lat)/2

			# Center the folium map at the centroid of the bounding box
            m.location=[centroid_lat,centroid_lng]

			# Fit the map view to the bounding box of the GeoJSON data
            m.fit_bounds([[min_lat,min_lng],[max_lat,max_lng]])
			
            # Define a style function
            def style_function(feature):
                return feature['properties'].get('style', {})
            
            # Add a new GeoJson layer to the map and layers attribute for each selected data object
            for geojson_data in selected_data_objects:
                layer = folium.GeoJson(geojson_data, style_function=style_function)
                layer.add_to(m)
                self.layers.append(layer)
                
                # Add a new option to the Listbox widget for the new layer
                self.visible_layers_listbox.insert(tk.END, geojson_data)
		
			# Create a GeoJsonPopup object
            popup = GeoJsonPopup(fields=fields)
		
			# Add a new GeoJson layer to the map with popups
            folium.GeoJson(geojson_data, style_function=style_function, popup=popup).add_to(m)
			
			# Add a title to the map
            title = self.title_entry.get()
            if title:
                title_html = f"""
                <div id="map-title" style="position: fixed; 
                                    bottom: 50px; left: 50px; height: 40px; 
                                    border:2px solid grey; z-index:9999; font-size:20px;
                                    background-color: white;
                                    ">  {title}
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
            
            #Add a layer control to the map
            if self.layer_control_var.get():
                LayerControl().add_to(m)
            
            # Display a file dialog window to select a file name and location for saving the folium map
            file_name = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Files", "*.html")])
            
            # Save the folium map to the selected file
            m.save(file_name)
            
            # Open the folium map in a web browser
            webbrowser.open(file_name)
            
        except Exception as e:
            print(f'An error occurred: {e}')
            
class LayerPropertiesWindow(tk.Toplevel):
    def __init__(self, master, main_window, layer):
        super().__init__(master)
        self.title('Layer Properties')
        self.main_window = main_window
        self.layer = layer
        self.create_widgets()
    
    def create_widgets(self):
        # Create Checkbutton widgets for selecting properties to include in popups
        self.property_vars = {}
        for property_name in self.get_property_names():
            var = tk.BooleanVar(self)
            checkbutton = tk.Checkbutton(self, text=property_name, variable=var)
            checkbutton.pack()
            self.property_vars[property_name] = var
        
        # Create a Button widget to apply the selected properties to the popups of the layer
        self.apply_button = tk.Button(self, text="Apply", command=self.apply_properties_to_popups)
        self.apply_button.pack()
    
    def get_property_names(self):
        # Get the first feature from the GeoJSON data of the layer
        feature = self.layer.data['features'][0]
        
        # Get the names of the properties from the feature
        property_names = list(feature['properties'].keys())
        
        return property_names
    
    def apply_properties_to_popups(self):
        # Create a list of fields to include in the popups
        fields = []
        for property_name, var in self.property_vars.items():
            if var.get():
                fields.append(property_name)
        
        # Create a GeoJsonPopup object
        popup = folium.GeoJsonPopup(fields=fields)
        
        # Update the popup of the layer
        self.layer.popup = popup
        
        # Close the window
        self.destroy()
