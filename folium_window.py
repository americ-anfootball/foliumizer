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
        self.top_layer = tk.StringVar()
        self.map_title = tk.StringVar()
        self.layer_control_var = tk.BooleanVar(value=True)
        self.create_widgets()
        self.geojson_data_list = []

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
        self.basemap_options = ['stamen toner', 'stamen terrain', 'stamen watercolor', 'cartodb positron', 'cartodb dark matter', 'openstreetmap', 'none']
        self.basemap_var = tk.StringVar(self)
        self.basemap_var.set(self.basemap_options[0])
        self.basemap_option_menu = tk.OptionMenu(self, self.basemap_var, *self.basemap_options)
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

        # Append the geojson_str data to the geojson_data_list variable
        geojson_data = json.loads(geojson_str)
        self.geojson_data_list.append(geojson_data)

    def create_map(self):
        styled_geojson_list = self.geojson_data_list

        top_layer = self.top_layer.get()

        active_layers = list(self.folium_listbox.get(0, tk.END))

        basemap_layer = self.basemap_var.get()

        if basemap_layer == 'none':
            m = folium.Map()
        elif basemap_layer in self.basemap_options:
            m = folium.Map(tiles=basemap_layer)
        else:
            raise ValueError(f"Invalid basemap layer: {basemap_layer}")

        top_layer_value = self.top_layer.get()

        min_lng, min_lat, max_lng, max_lat = float('inf'), float('inf'), float('-inf'), float('-inf')

        def style_function(feature):
            style = feature['properties'].get('style', {})
            print(f"Feature: {feature}")
            print(f"Style: {style}")
            return style

        for i, geojson_data in enumerate(styled_geojson_list):
            layer_min_lng, layer_min_lat, layer_max_lng, layer_max_lat = calculate_bounding_box(geojson_data)

            min_lng = min(min_lng, layer_min_lng)
            min_lat = min(min_lat, layer_min_lat)
            max_lng = max(max_lng, layer_max_lng)
            max_lat = max(max_lat, layer_max_lat)

            if i == top_layer_value:
                folium.GeoJson(geojson_data, style_function=style_function, overlay=True, show=True).add_to(m)
            else:
                folium.GeoJson(geojson_data, style_function=style_function, overlay=True, show=False).add_to(m)

        centroid_lng=(min_lng+max_lng)/2
        centroid_lat=(min_lat+max_lat)/2

        m.location=[centroid_lat,centroid_lng]

        m.fit_bounds([[min_lat,min_lng],[max_lat,max_lng]])

        title = self.map_title.get()

        title = self.logic.gui.map_title_entry.get()
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

        if self.layer_control_var.get():
            LayerControl().add_to(m)

        file_name = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Files", "*.html")])

        m.save(file_name)

        webbrowser.open(file_name)

        return m
