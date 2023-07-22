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
        self.top_layer = tk.StringVar(value="Layer 1")  # Initialize self.top_layer with a default value
        self.map_title = tk.StringVar()
        self.layer_control_var = tk.BooleanVar(value=True)
        self.create_widgets()
        self.geojson_data_list = []
        self.geojson_layers = []  # Create a new attribute to store references to the GeoJson layers
        self.feature_groups = []
        self.m = folium.Map()
        
        # Set maximum window size
        self.wm_maxsize(self.winfo_screenwidth(), self.winfo_screenheight())

    def create_widgets(self):        
        # Create a top frame to hold the Listbox and Scrollbars
        self.listbox_frame = tk.Frame(self)
        self.listbox_frame.grid(row=1, column=0, padx=5, pady=5)

        # Create a title for the listbox widget:
        self.layer_listbox_label = tk.Label(self.listbox_frame, text="Available Layers")
        self.layer_listbox_label.grid(row=0, column=0, padx=5, pady=5)

        # Create a Listbox widget to display the passed data
        self.folium_listbox = tk.Listbox(self.listbox_frame, selectmode=tk.SINGLE, exportselection=False)#, xscrollcommand=self.xscroll.set, yscrollcommand=self.yscroll.set)
        self.folium_listbox.grid(row=1, column=0)

        # Create a label for the layer title entry
        self.layer_title_label = tk.Label(self.listbox_frame, text="Layer Title:")
        self.layer_title_label.grid(row=3, column=0, padx=5, pady=5)

        # Create an Entry widget for the layer title
        self.layer_title_entry = tk.Entry(self.listbox_frame)
        self.layer_title_entry.grid(row=3, column=1, padx=5, pady=5)

        # Create a button for updating the name for the selected layer
        self.update_popup_properties_button = tk.Button(self.listbox_frame,text="Apply Name to Selected Layer",command=self.update_layer_name)
        self.update_popup_properties_button.grid(row=3,column=3, padx=5,pady=5)

        # Create a label and OptionMenu for the top layer selection
        self.top_layer_label = tk.Label(self.listbox_frame, text="Top Layer:")
        self.top_layer_label.grid(row=4, column=3, padx=5, pady=5)
        self.top_layer_menu = tk.OptionMenu(self.listbox_frame,self.top_layer,"")
        self.top_layer_menu.grid(row=4,column=4,padx=5,pady=5)
        print(f"Creating OptionMenu for top layer selection with variable: {self.top_layer.get()}")  # Print the value of self.top_layer
        
        # Create a label for the popup properties Listbox
        self.popup_properties_label = tk.Label(self.listbox_frame, text="Select One or More Popup Properties:")
        self.popup_properties_label.grid(row=0, column=3, padx=5, pady=5)

        # Create a Listbox for selecting the popup properties
        self.popup_properties_listbox = tk.Listbox(self.listbox_frame, selectmode=tk.MULTIPLE)
        self.popup_properties_listbox.grid(row=1, column=3, padx=5, pady=5)

        # Create a button for updating the popup properties for the selected layer
        self.update_popup_properties_button = tk.Button(self.listbox_frame,text="Apply Selected Popup Properties for Selected Layer",command=self.update_popup_properties)
        self.update_popup_properties_button.grid(row=2,column=3,padx=5,pady=5)

        # Create a label for the map title entry
        self.map_title_label = tk.Label(self.listbox_frame, text="Map Title:")
        self.map_title_label.grid(row=5, column=0, padx=5, pady=5)

        # Create an Entry widget for the map title
        self.map_title_entry = tk.Entry(self.listbox_frame, textvariable=self.map_title)
        self.map_title_entry.grid(row=5, column=1, padx=5, pady=5)

        # Create a label and OptionMenu for the map title placement
        self.title_placement_label = tk.Label(self.listbox_frame, text="Title Placement:")
        self.title_placement_label.grid(row=5, column=3, padx=5, pady=5)
        self.title_placement_var = tk.StringVar(value="top-center")
        self.title_placement_options = ["top-left", "top-right", "bottom-left", "bottom-right", "top-center", "bottom-center"]
        self.title_placement_menu = tk.OptionMenu(self.listbox_frame, self.title_placement_var, *self.title_placement_options)
        self.title_placement_menu.grid(row=5, column=4, padx=5, pady=5)

        # Create a label and OptionMenu for the map title border color
        self.title_border_color_label = tk.Label(self.listbox_frame, text="Title Border Color:")
        self.title_border_color_label.grid(row=6, column=0, padx=5, pady=5)
        self.title_border_color_var = tk.StringVar(value="grey")
        self.title_border_color_options = ["black", "grey", "white", "red", "green", "blue"]
        self.title_border_color_menu = tk.OptionMenu(self.listbox_frame, self.title_border_color_var, *self.title_border_color_options)
        self.title_border_color_menu.grid(row=6, column=1, padx=5, pady=5)
        
        # Create a label and OptionMenu for the map title border size
        self.title_border_size_label = tk.Label(self.listbox_frame, text="Title Border Weight (in Pixels):")
        self.title_border_size_label.grid(row=7, column=0, padx=5, pady=5)
        
        # Create a variable to hold the border size value
        self.title_border_size_var = tk.IntVar(value=1)

        # Create a Scale widget for the map title border size
        self.title_border_size_scale = tk.Scale(self.listbox_frame, from_=1, to=5, orient=tk.HORIZONTAL, variable=self.title_border_size_var)
        self.title_border_size_scale.grid(row=7, column=1, columnspan=2, padx=5, pady=5)

        # Create a label and Entry for the map title font size
        self.title_font_size_label = tk.Label(self.listbox_frame, text="Title Font Size:")
        self.title_font_size_label.grid(row=7, column=3, padx=5, pady=5)

        # Create a variable to hold the font size value
        self.title_font_size_var = tk.IntVar(value=20)

        # Create a Scale widget for the map title font size
        self.title_font_size_scale = tk.Scale(self.listbox_frame, from_=8, to=72, orient=tk.HORIZONTAL, variable=self.title_font_size_var)
        self.title_font_size_scale.grid(row=7, column=4, columnspan=2, padx=5, pady=5)

        # Create a label and OptionMenu for the map title font color
        self.title_font_color_label = tk.Label(self.listbox_frame, text="Title Font Color:")
        self.title_font_color_label.grid(row=8, column=0, padx=5, pady=5)
        self.title_font_color_var = tk.StringVar(value="black")
        self.title_font_color_options = ["black", "grey", "white", "red", "green", "blue"]
        self.title_font_color_menu = tk.OptionMenu(self.listbox_frame,self.title_font_color_var,*self.title_font_color_options)
        self.title_font_color_menu.grid(row=8,column=1,padx=5,pady=5)

        # Create a label and OptionMenu for the map title background color
        self.title_bg_color_label = tk.Label(self.listbox_frame, text="Title Background Color:")
        self.title_bg_color_label.grid(row=8, column=3, padx=5, pady=5)
        self.title_bg_color_var = tk.StringVar(value="white")
        self.title_bg_color_options = ["black", "grey", "white", "red", "green", "blue"]
        self.title_bg_color_menu = tk.OptionMenu(self.listbox_frame, self.title_bg_color_var, *self.title_bg_color_options)
        self.title_bg_color_menu.grid(row=8, column=4, padx=5, pady=5)

        # Create a label and OptionMenu widget for selecting the folium basemap layer
        self.title_bg_color_label = tk.Label(self.listbox_frame, text="Select Basemap Layer:")
        self.title_bg_color_label.grid(row=4, column=0, padx=5, pady=5)        
        self.basemap_options = ['stamen toner', 'stamen terrain', 'stamen watercolor', 'cartodb positron', 'cartodb dark matter', 'openstreetmap', 'none']
        self.basemap_var = tk.StringVar(self)
        self.basemap_var.set(self.basemap_options[0])
        self.basemap_option_menu = tk.OptionMenu(self.listbox_frame, self.basemap_var, *self.basemap_options)
        self.basemap_option_menu.grid(row=4, column=1, padx=5, pady=5)

        # Create a button to create the folium map from active layers
        self.create_map_button = tk.Button(self.listbox_frame, text="Create Folium Map from Active Layers", command=self.create_map)
        self.create_map_button.grid(row=9,columnspan=2, padx=5, pady=5)

        # Configure the bottom frame grid to resize properly
        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)

    def add_layer(self, geojson_str):
        # Increment the layer count
        self.layer_count += 1

        # Retrieve the layer title from the Entry widget
        layer_title = self.layer_title_entry.get()
        if not layer_title:
            layer_title = f"Layer {self.layer_count}"

        # Insert the alias into the folium listbox
        alias = f"Layer {self.layer_count}"
        self.folium_listbox.insert(tk.END, alias)

        # Update or create the top layer menu and label
        menu = self.top_layer_menu["menu"]
        menu.add_command(label=alias, command=lambda value=alias: self.top_layer.set(value))
        if not menu.index("end"):
            self.top_layer.set(alias)  # Set the top layer to the first item in the menu
            if menu.entrycget(0, "label") == "Layer 1":
                menu.delete(0)  # Remove the default "Layer 1" entry from the menu
            
        # Append the geojson_str data to the geojson_data_list variable
        geojson_data = json.loads(geojson_str)
        self.geojson_data_list.append(geojson_data)

        # Create a new FeatureGroup for this layer
        feature_group = folium.FeatureGroup(name=layer_title)
        
        # Add the GeoJson layer to the FeatureGroup
        feature_group.add_child(folium.GeoJson(geojson_str))
        
        # Add this FeatureGroup to the map
        feature_group.add_to(self.m)

        # Append a reference to the FeatureGroup to the feature_groups list
        self.feature_groups.append(feature_group)

    def update_layer_name(self):
        # Get the selected layer index from the folium_listbox
        selected_index = self.folium_listbox.curselection()
        if not selected_index:
            return  # No layer is selected
        selected_index = selected_index[0]

        # Get the new layer name from the layer_title_entry widget
        new_layer_name = self.layer_title_entry.get()
        if not new_layer_name:
            return  # No new layer name is entered

        # Update the folium_listbox with the new layer name
        self.folium_listbox.delete(selected_index)
        self.folium_listbox.insert(selected_index, new_layer_name)

        # Update the top_layer_menu with the new layer name
        menu = self.top_layer_menu["menu"]
        menu.entryconfig(selected_index, label=new_layer_name)
        menu.entryconfig(selected_index, command=lambda value=new_layer_name: self.top_layer.set(value))

        # Remove any default layer names that are not present in the folium_listbox
        for i in range(menu.index("end") + 1):
            label = menu.entrycget(i, "label")
            if label.startswith("Layer ") and label not in self.folium_listbox.get(0, "end"):
                menu.delete(i)

        # Redraw the OptionMenu widget
        self.top_layer_menu.update()

        # Update the feature group with the new layer name
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

        top_layer_value = self.top_layer.get()
        top_layer_index = self.folium_listbox.get(0, "end").index(top_layer_value)

        active_layers = list(self.folium_listbox.get(0, tk.END))

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

            show_layer = (i == top_layer_index)

            geojson_layer = folium.GeoJson(geojson_data, style_function=style_function, overlay=True, show=show_layer)

            layer_name = self.folium_listbox.get(i)
            feature_group = folium.FeatureGroup(name=layer_name, show=show_layer)
            print(f"Creating FeatureGroup with name: {feature_group.layer_name}")  # Print the layer name

            feature_group.add_child(geojson_layer)

            self.geojson_layers.append(geojson_layer)

            def popup_style_function(feature):
                return {'fillOpacity': 0, 'weight': 0}

            for feature in geojson_data["features"]:
                if "popupProperties" in feature["properties"]:
                    popup_properties = feature["properties"]["popupProperties"]

                    popup_html = "<table>"
                    for prop in popup_properties:
                        if prop != "popupProperties":
                            value = feature["properties"].get(prop, "")
                            popup_html += f"<tr><td><b>{prop}:</b></td><td>{value}</td></tr>"
                    popup_html += "</table>"

                    feature_layer = folium.GeoJson(feature, style_function=popup_style_function)

                    feature_layer.add_child(folium.Popup(popup_html))

                    geojson_layer.add_child(feature_layer)

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
            print("Adding LayerControl to map")  # Print a message when the LayerControl is added

        file_name = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Files", "*.html")])

        m.save(file_name)

        webbrowser.open(file_name)

        return m
        
