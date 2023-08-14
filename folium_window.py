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
from typing import Any, List, Tuple


class FoliumWindowLogic:
    def __init__(self, gui=None, working_object_a=None, working_object_b=None):
        self.gui = gui
        self.working_object_a = working_object_a
        self.working_object_b = working_object_b

    def get_all_styled_geojson(self):
        # Initialize a list to hold the styled GeoJSON data for each layer
        styled_geojson_list = []

        # Iterate over the GeoJSON data in the geojson_data_list variable
        for i, geojson_data in enumerate(self.gui.geojson_data_list):
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
        self.layer_count = 0
        self.map_title = tk.StringVar()
        self.layer_control_var = tk.BooleanVar(value=True)
        self.create_widgets()
        self.geojson_data_list = []
        self.geojson_layers = []  # Create a new attribute to store references to the GeoJson layers
        self.feature_groups = []
        self.m = folium.Map()

    def create_widgets(self):        
        # Create a title for the listbox widget:
        self.layer_listbox_label = tk.Label(self, text="Available Layers")
        self.layer_listbox_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        # Create a top frame to hold the Listbox and Scrollbars
        self.listbox_frame = tk.Frame(self)
        self.listbox_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # Create the vertical scrollbar
        self.yscroll = tk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL)
        self.yscroll.grid(row=0, column=1)

        # Create the horizontal scrollbar
        self.xscroll = tk.Scrollbar(self.listbox_frame, orient=tk.HORIZONTAL)
        self.xscroll.grid(row=1, column=0)

        # Create a Listbox widget to display the passed data
        self.folium_listbox = tk.Listbox(self.listbox_frame, selectmode=tk.SINGLE, exportselection=False, xscrollcommand=self.xscroll.set, yscrollcommand=self.yscroll.set)
        self.folium_listbox.grid(row=0, column=0)

        # Attach the scrollbars to the Listbox
        self.yscroll.config(command=self.folium_listbox.yview)
        self.xscroll.config(command=self.folium_listbox.xview)

        # Configure the top frame grid to resize properly
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Create a middle frame to hold the widgets
        self.middle_frame = tk.Frame(self)
        self.middle_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Create a label for the layer title entry
        self.layer_title_label = tk.Label(self.middle_frame, text="Layer Title:")
        self.layer_title_label.grid(row=0, column=0, padx=5, pady=5)

        # Create an Entry widget for the layer title
        self.layer_title_entry = tk.Entry(self.middle_frame)
        self.layer_title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Create a button for updating the popup properties for the selected layer
        self.update_layer_name_button = tk.Button(self.middle_frame,text="Apply Name to Selected Layer",command=self.update_layer_name)
        self.update_layer_name_button.grid(row=1,column=1, padx=5,pady=5)

        # Create a label for the popup properties Listbox
        self.popup_properties_label = tk.Label(self.middle_frame, text="Select One or More Popup Properties:")
        self.popup_properties_label.grid(row=3, column=0, padx=5, pady=5)

        # Create a Listbox for selecting the popup properties
        self.popup_properties_listbox = tk.Listbox(self.middle_frame, selectmode=tk.MULTIPLE)
        self.popup_properties_listbox.grid(row=3, column=1, padx=5, pady=5)

        # Create a button for updating the popup properties for the selected layer
        self.update_popup_properties_button = tk.Button(self.middle_frame,text="Apply Selected Popup Properties for Selected Layer",command=self.update_popup_properties)
        self.update_popup_properties_button.grid(row=4,columnspan=2,padx=5,pady=5)

        # Configure the middle frame grid to resize properly
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Create a bottom frame to hold the widgets
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.grid(row=10, column=0, columnspan=2, padx=5, pady=5)

        # Create a label for the map title entry
        self.map_title_label = tk.Label(self.bottom_frame, text="Map Title:")
        self.map_title_label.grid(row=0, column=0, padx=5, pady=5)

        # Create an Entry widget for the map title
        self.map_title_entry = tk.Entry(self.bottom_frame, textvariable=self.map_title)
        self.map_title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Create a label and OptionMenu for the map title placement
        self.title_placement_label = tk.Label(self.bottom_frame, text="Title Placement:")
        self.title_placement_label.grid(row=1, column=0, padx=5, pady=5)
        self.title_placement_var = tk.StringVar(value="top-center")
        self.title_placement_options = ["top-left", "top-right", "bottom-left", "bottom-right", "top-center", "bottom-center"]
        self.title_placement_menu = tk.OptionMenu(self.bottom_frame, self.title_placement_var, *self.title_placement_options)
        self.title_placement_menu.grid(row=1, column=1, padx=5, pady=5)

        # Create a label and OptionMenu for the map title border color
        self.title_border_color_label = tk.Label(self.bottom_frame, text="Title Border Color:")
        self.title_border_color_label.grid(row=2, column=0, padx=5, pady=5)
        self.title_border_color_var = tk.StringVar(value="grey")
        self.title_border_color_options = ["black", "grey", "white", "red", "green", "blue"]
        self.title_border_color_menu = tk.OptionMenu(self.bottom_frame, self.title_border_color_var, *self.title_border_color_options)
        self.title_border_color_menu.grid(row=2, column=1, padx=5, pady=5)
        
        # Create a label and OptionMenu for the map title border size
        self.title_border_size_label = tk.Label(self.bottom_frame, text="Title Border Weight (in Pixels):")
        self.title_border_size_label.grid(row=3, column=0, padx=5, pady=5)
        
        # Create a variable to hold the border size value
        self.title_border_size_var = tk.IntVar(value=1)

        # Create a Scale widget for the map title border size
        self.title_border_size_scale = tk.Scale(self.bottom_frame, from_=1, to=5, orient=tk.HORIZONTAL, variable=self.title_border_size_var)
        self.title_border_size_scale.grid(row=3, column=1, columnspan=2, padx=5, pady=5)

        # Create a label and Entry for the map title font size
        self.title_font_size_label = tk.Label(self.bottom_frame, text="Title Font Size:")
        self.title_font_size_label.grid(row=4, column=0, padx=5, pady=5)

        # Create a variable to hold the font size value
        self.title_font_size_var = tk.IntVar(value=20)

        # Create a Scale widget for the map title font size
        self.title_font_size_scale = tk.Scale(self.bottom_frame, from_=8, to=72, orient=tk.HORIZONTAL, variable=self.title_font_size_var)
        self.title_font_size_scale.grid(row=4, column=1, columnspan=2, padx=5, pady=5)

        # Create a label and OptionMenu for the map title font color
        self.title_font_color_label = tk.Label(self.bottom_frame, text="Title Font Color:")
        self.title_font_color_label.grid(row=5, column=0, padx=5, pady=5)
        self.title_font_color_var = tk.StringVar(value="black")
        self.title_font_color_options = ["black", "grey", "white", "red", "green", "blue"]
        self.title_font_color_menu = tk.OptionMenu(self.bottom_frame,self.title_font_color_var,*self.title_font_color_options)
        self.title_font_color_menu.grid(row=5,column=1,padx=5,pady=5)

        # Create a label and OptionMenu for the map title background color
        self.title_bg_color_label = tk.Label(self.bottom_frame, text="Title Background Color:")
        self.title_bg_color_label.grid(row=6, column=0, padx=5, pady=5)
        self.title_bg_color_var = tk.StringVar(value="white")
        self.title_bg_color_options = ["black", "grey", "white", "red", "green", "blue"]
        self.title_bg_color_menu = tk.OptionMenu(self.bottom_frame, self.title_bg_color_var, *self.title_bg_color_options)
        self.title_bg_color_menu.grid(row=6, column=1, padx=5, pady=5)

        # Create a label and OptionMenu widget for selecting the folium basemap layer
        self.title_bg_color_label = tk.Label(self.bottom_frame, text="Select Basemap Layer:")
        self.title_bg_color_label.grid(row=7, column=0, padx=5, pady=5)        
        self.basemap_options = ['stamen toner', 'stamen terrain', 'stamen watercolor', 'cartodb positron', 'cartodb dark matter', 'openstreetmap', 'none']
        self.basemap_var = tk.StringVar(self)
        self.basemap_var.set(self.basemap_options[0])
        self.basemap_option_menu = tk.OptionMenu(self.bottom_frame, self.basemap_var, *self.basemap_options)
        self.basemap_option_menu.grid(row=7, column=1, padx=5, pady=5)

        # Configure the bottom frame grid to resize properly
        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)

        # Create a button to create the folium map from active layers
        self.create_map_button = tk.Button(self, text="Create Folium Map from Active Layers", command=self.create_map)
        self.create_map_button.grid(row=12,columnspan=2, padx=5, pady=5)

    def add_layer(self, geojson_str):
        self.layer_count += 1
        layer_title = self.layer_title_entry.get()
        if not layer_title:
            layer_title = f"Layer {self.layer_count}"
        self.folium_listbox.insert(tk.END, layer_title)
        geojson_data = json.loads(geojson_str)
        self.geojson_data_list.append(geojson_data)
        feature_group = folium.FeatureGroup(name=layer_title)
        feature_group.add_child(folium.GeoJson(geojson_str))
        feature_group.add_to(self.m)
        self.feature_groups.append(feature_group)

    def update_layer_name(self):
        selected_index = self.folium_listbox.curselection()
        if not selected_index:
            return  # No layer is selected
        selected_index = selected_index[0]
        new_layer_name = self.layer_title_entry.get()
        if not new_layer_name:
            return  # No new layer name is entered
        self.folium_listbox.delete(selected_index)
        self.folium_listbox.insert(selected_index, new_layer_name)
        
        # Update the LayerControl widget of the output Folium map with the new layer name
        if self.feature_groups:
            feature_group = self.feature_groups[selected_index]
            feature_group.layer_name = new_layer_name

    def update_popup_properties(self):
        # Get the index of the currently selected layer
        selected_layer_index = self.folium_listbox.curselection()[0]
        
        # Get the list of selected properties from the Listbox
        selected_properties = [self.popup_properties_listbox.get(i) for i in self.popup_properties_listbox.curselection()]
        
        # Update the popup properties for each feature in the selected layer
        geojson_data = self.geojson_data_list[selected_layer_index]
        for feature in geojson_data["features"]:
            if "properties" not in feature:
                feature["properties"] = {}
            feature["properties"]["popupProperties"] = selected_properties
        
        # Get the list of available properties for the selected layer
        available_properties = set()
        for feature in geojson_data["features"]:
            available_properties.update(feature["properties"].keys())
        
        # Update the Listbox with the available properties
        self.popup_properties_listbox.delete(0, tk.END)
        for prop in sorted(available_properties):
            self.popup_properties_listbox.insert(tk.END, prop)
        
    def create_map(self):
        styled_geojson_list = self.geojson_data_list
        
        # Get the selected layer from the folium_listbox
        selected_layer = self.folium_listbox.get(tk.ANCHOR)
        
        active_layers = list(self.folium_listbox.get(0, tk.END))
        
        for i, layer_name in enumerate(active_layers):
            feature_group = self.feature_groups[i]
            if layer_name == selected_layer:
                feature_group.show = True
            else:
                feature_group.show = False
                
        basemap_layer = self.basemap_var.get()
        
        if basemap_layer == 'none':
            m = folium.Map()
        elif basemap_layer in self.basemap_options:
            m = folium.Map(tiles=basemap_layer)
        else:
            raise ValueError(f"Invalid basemap layer: {basemap_layer}")
            
        min_lng, min_lat, max_lng, max_lat = float('inf'), float('inf'), float('-inf'), float('-inf')
        
        def style_function(feature):
            style = feature['properties'].get('style', {})
            return style
            
        for i, geojson_data in enumerate(styled_geojson_list):
            layer_min_lng, layer_min_lat, layer_max_lng, layer_max_lat = calculate_bounding_box(geojson_data)

            min_lng = min(min_lng, layer_min_lng)
            min_lat = min(min_lat, layer_min_lat)
            max_lng = max(max_lng, layer_max_lng)
            max_lat = max(max_lat, layer_max_lat)
            
            # Create a GeoJson layer for this data
            geojson_layer = folium.GeoJson(geojson_data, style_function=style_function, overlay=True)
            
            # Create a new FeatureGroup for this layer using the updated layer name from the Listbox
            feature_group = folium.FeatureGroup(name=active_layers[i])
            
            # Add the GeoJson layer to the FeatureGroup
            feature_group.add_child(geojson_layer)
            
            # Append a reference to the GeoJson layer to the geojson_layers list
            self.geojson_layers.append(geojson_layer)
            			
            def popup_style_function(feature):
                return {'fillOpacity': 0, 'weight': 0}
                 					
            # Add popups to this layer
            for feature in geojson_data["features"]:
                if "popupProperties" in feature["properties"]:
                    popup_properties = feature["properties"]["popupProperties"]
                    
                    popup_html = "<table>"
                    for prop in popup_properties:
                        if prop != "popupProperties":
                            value = feature["properties"].get(prop, "")
                            popup_html += f"<tr><td><b>{prop}:</b></td><td>{value}</td></tr>"
                    popup_html += "</table>"
                    
                    # Create a new GeoJson object for this feature
                    feature_layer = folium.GeoJson(feature, style_function=popup_style_function)
                    
                    # Add the popup to this feature
                    feature_layer.add_child(folium.Popup(popup_html))
                    
                    # Add this feature to the layer
                    geojson_layer.add_child(feature_layer)
                    			
            # Add this FeatureGroup to the map
            feature_group.add_to(m)

        centroid_lng=(min_lng+max_lng)/2
        centroid_lat=(min_lat+max_lat)/2
        
        m.location=[centroid_lat,centroid_lng]
        
        m.fit_bounds([[min_lat,min_lng],[max_lat,max_lng]])
        
        title = self.map_title.get()
        if title:
            placement = self.title_placement_var.get()
            border_size = self.title_border_size_var.get()
            border_color = self.title_border_color_var.get()
            font_size = self.title_font_size_var.get() 
            font_color = self.title_font_color_var.get()
            bg_color = self.title_bg_color_var.get()
            
            if placement == "top-left":
                position = f"top: 25px; left: 25px;"
            elif placement == "top-right":
                position = f"top: 25px; right: 25px;"
            elif placement == "bottom-left":
                position = f"bottom: 25px; left: 25px;"
            elif placement == "bottom-right":
                position = f"bottom: 25px; right: 25px;"
            elif placement == "top-center":
                position = f"top: 25px; left: 50%; transform: translateX(-50%);"
            elif placement == "bottom-center":
                position = f"bottom: 25px; left: 50%; transform: translateX(-50%);"

            title_html = f"""
            <div id="map-title" style="position: fixed; {position} border:{border_size}px solid {border_color}; z-index:9999; font-size:{font_size}px; color:{font_color}; background-color: {bg_color};">  {title}
            </div>
            <script>
                // Get the map title element
                var mapTitle = document.getElementById('map-title');
                
                // Measure the width and height of the title text
                var canvas = document.createElement('canvas');
                var context = canvas.getContext('2d');
                context.font = '{font_size}px sans-serif';
                var metrics = context.measureText(mapTitle.textContent);
                
                // Set the width and height of the map title element
                mapTitle.style.width = (metrics.width + 20) + 'px';
                mapTitle.style.height = (metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent + 20) + 'px';
            </script>
            """
            m.get_root().html.add_child(folium.Element(title_html))
            
        if self.layer_control_var.get():
            LayerControl().add_to(m)
            
        file_name = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Files", "*.html")])
        
        m.save(file_name)
        
        webbrowser.open(file_name)
        
        return m
