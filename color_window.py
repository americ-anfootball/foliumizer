import geopandas as gpd
import json
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from color_utils import generate_color_ramp, hsb_to_rgb, generate_and_display_color_palette, set_color_ramp, get_styled_geojson, generate_styled_geojson, reverse_color_ramp, get_categorical_color_map, generate_categorical_color_map
from folium_window import FoliumWindowLogic, FoliumWindowGUI
from matplotlib.colors import ListedColormap
from tkinter import ttk
from typing import Any, List, Tuple


class ColorWindowLogic:
    def __init__(self, working_object_a=None, working_object_b=None):
        self.working_object_a = working_object_a
        self.working_object_b = working_object_b
        self.color_ramp = None

    def generate_color_ramp(self, hue1: int, hue2: int, bins: int, ramp_type: str) -> List[Tuple[int, int, int]]:
        return generate_color_ramp(hue1, hue2, bins, ramp_type)

    def hsb_to_rgb(self, h: float, s: float, b: float) -> Tuple[float, float, float]:
        return hsb_to_rgb(h, s, b)

    def generate_and_display_color_palette(self, canvas: Any, apply_button: Any, hue1: int, hue2: int, bins: int, ramp_type: str, reverse_color_ramp_var: tk.BooleanVar) -> List[Tuple[int, int, int]]:
        return generate_and_display_color_palette(canvas, apply_button, hue1, hue2, bins, ramp_type, reverse_color_ramp_var)

    def set_color_ramp(self, color_ramp_listbox: Any, text_widget_c: Any) -> str:
        return set_color_ramp(color_ramp_listbox, text_widget_c)

    def get_styled_geojson(self, geojson_data: Any, selected_property: str, classification_method: str, bins: int, color_ramp: List[Tuple[int, int, int]]) -> str:
        return get_styled_geojson(geojson_data, selected_property, classification_method, bins, color_ramp)

    def generate_styled_geojson(self, color_ramp: List[Tuple[int, int, int]], bins: int, classification_method: str) -> str:
        return generate_styled_geojson(color_ramp, bins, classification_method)
        
    def get_categorical_color_map(self, geojson_data, selected_property, color_map):
        return get_categorical_color_map(geojson_data, selected_property, color_map)
        
    def generate_categorical_color_map(self, working_object_a, working_object_b, color_map):
        return generate_categorical_color_map(working_object_a, working_object_b, color_map)


class ColorWindowGUI(tk.Toplevel):
    def __init__(self, master=None, app=None, logic=None):
        super().__init__(master)
        self.app = app
        self.logic = logic
        self.apply_button_clicked = False
        self.create_widgets()

    def create_widgets(self):
        try:
            # create the hue label and slider
            self.hue_label = tk.Label(self, text='Hue 1:')
            self.hue_label.grid(row=0, columnspan=2)
            self.hue_slider = tk.Scale(self, from_=0, to=360, orient=tk.HORIZONTAL)
            self.hue_slider.set(0)
            self.hue_slider.grid(row=1, columnspan=2)

            # create the hue entry field
            self.hue_entry_var = tk.StringVar(value='0')
            self.hue_entry_var.trace('w', lambda *args: self.update_scale_from_entry(self.hue_slider, self.hue_entry_var.get()))
            self.hue_entry = tk.Entry(self, textvariable=self.hue_entry_var)
            self.hue_entry.grid(row=2, columnspan=2)

            # create the second hue label and slider
            self.hue2_label = tk.Label(self, text='Hue 2:')
            self.hue2_slider = tk.Scale(self, from_=0, to=360, orient=tk.HORIZONTAL)
            self.hue2_slider.set(0)
            self.hue2_entry_var = tk.StringVar(value='0')
            self.hue2_entry_var.trace('w', lambda *args: update_scale_from_entry(self.hue2_slider, self.hue2_entry_var.get()))
            self.hue2_entry = tk.Entry(self, textvariable=self.hue2_entry_var)

            # create the bins label and slider
            self.bins_label = tk.Label(self, text='Number of bins:')
            self.bins_label.grid(row=3,columnspan=2)
            self.bins_slider = tk.Scale(self, from_=2, to=20, orient=tk.HORIZONTAL)
            self.bins_slider.set(2)
            self.bins_slider.grid(row=4,columnspan=2)

            # create the ramp type label and radio buttons
            self.ramp_type_label = tk.Label(self,text='Color ramp type:')
            self.ramp_type_label.grid(row=5,columnspan=2)
            self.ramp_type_var = tk.StringVar(value='sequential')
            self.sequential_ramp_button = tk.Radiobutton(self,text='Sequential',variable=self.ramp_type_var,value='sequential', command=lambda: self.update_hue2_slider_state(self.hue2_label, self.hue2_slider, self.hue2_entry, self.ramp_type_var.get()))
            self.sequential_ramp_button.grid(row=6,columnspan=2)
            
            self.diverging_ramp_button = tk.Radiobutton(self,text='Diverging',variable=self.ramp_type_var,value='diverging', command=lambda: self.update_hue2_slider_state(self.hue2_label, self.hue2_slider, self.hue2_entry, self.ramp_type_var.get()))
            self.diverging_ramp_button.grid(row=7,columnspan=2)
            self.reverse_color_ramp_var = tk.BooleanVar()
            self.reverse_color_ramp_checkbox = tk.Checkbutton(self, text="Reverse Color Ramp", variable=self.reverse_color_ramp_var)
            self.reverse_color_ramp_checkbox.grid(row=8,columnspan=2)

            self.reverse_color_ramp_var.trace("w", lambda *args: self.on_reverse_color_ramp_changed())

            # update the state of the second hue slider
            self.update_hue2_slider_state(self.hue2_label, self.hue2_slider, self.hue2_entry, self.ramp_type_var.get())

            # create the canvas
            self.canvas = tk.Canvas(self, width=200, height=50)
            self.canvas.grid(row=9,columnspan=2)

            # create the classification method label and option menu
            self.classification_method_label = tk.Label(self, text='Classification method:')
            self.classification_method_label.grid(row=10,column=0)
            self.classification_method_var = tk.StringVar(value='quantiles')
            self.classification_method_options = ['quantiles', 'equal_interval', 'standard_deviation']
            self.classification_method_menu = tk.OptionMenu(self, self.classification_method_var, *self.classification_method_options)
            self.classification_method_menu.grid(row=10,column=1)

            color_ramp = None

            # create the generate and apply buttons
            self.generate_button = tk.Button(self, text='Generate Color Palette', command=self.on_generate_button_click)
            self.generate_button.grid(row=11,columnspan=2)

            self.apply_button = tk.Button(self, text='Preview Color Palette', state=tk.DISABLED, command=self.on_apply_button_click)
            self.apply_button.grid(row=12,columnspan=2)

            self.pass_data_button = tk.Button(self, text='Add this Layer to Folium Map', state=tk.DISABLED, command=self.on_pass_data_button_click)
            self.pass_data_button.grid(row=13,columnspan=2)
        except Exception as e:
            print(f"An error occurred while creating widgets: {e}")

        # Create a BooleanVar to track the state of the check box
        self.categorical_color_map_var = tk.BooleanVar()

        # Create a check box for enabling/disabling the categorical color map
        self.categorical_color_map_check_box = tk.Checkbutton(self, text="Categorical Color Map", variable=self.categorical_color_map_var)
        self.categorical_color_map_check_box.grid(row=14, columnspan=2)

        # Create a Treeview for displaying the unique values and their colors
        self.unique_values_treeview = ttk.Treeview(self, columns=['color'], show='tree')
        self.unique_values_treeview.grid(row=0, column=5, columnspan=2)

        # Function to populate the Treeview with unique values
        def populate_treeview():
            # Clear the Treeview
            self.unique_values_treeview.delete(*self.unique_values_treeview.get_children())

            # Get the unique values of the working_object_b variable
            unique_values = self.logic.working_object_a[self.logic.working_object_b].unique()

            # Insert an item for each unique value
            for value in unique_values:
                self.unique_values_treeview.insert('', 'end', text=value)

        # Call the populate_treeview function whenever the check box is toggled
        self.categorical_color_map_var.trace('w', lambda *args: populate_treeview())

        # Create a PhotoImage object for each color in your color map
        color_images = {}
        for color_name, color_value in color_map.items():
            image = tk.PhotoImage(width=40, height=20)
            image.put(color_value, to=(0, 0, 40, 20))
            color_images[color_name] = image

        # Insert an item for each color in your color map
        for color_name, color_image in color_images.items():
            self.unique_values_treeview.insert('', 'end', text=color_name, image=color_image)

        # Create a dropdown menu for selecting the color
        color_options = [
            'black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 
            'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 
            'aqua', 'aliceblue', 'aquamarine', 'azure', 'beige', 'bisque', 
            'blanchedalmond', 'blueviolet', 'brown', 'burlywood', 'cadetblue',
            'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 
            'crimson', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 
            'darkgreen', 'darkkhaki', 'darkmagenda', 'darkolivegreen', 
            'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 
            'darkslateblue', 'darkslategrey', 'darkturquoise', 'darkviolet', 
            'deeppink', 'deepskyblue', 'dimgray', 'dodgerblue', 'firebrick', 
            'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro', 'ghostwhite', 
            'gold', 'goldenrod', 'honeydew', 'hotpink', 'indianred', 'indigo', 
            'khaki', 'lavender', 'lavenderblush', 'lemonchiffon', 'lighblue', 
            'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray', 
            'lightgreen', 'lightpink', 'lightsalmon', 'lightseagreen', 
            'lightskyblue', 'lightslategray', 'lightsteelblue', 'lightyellow', 
            'lime', 'limegreen', 'mediumaquamarine', 'mediumblue', 
            'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 
            'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 
            'midnightblue', 'mintcream', 'mistyrose', 'mocassin', 'navajowhite', 
            'navy', 'oldlace', 'olivedrab', 'orangered', 'orchid', 
            'palegoldenrod', 'paleturquoise', 'palevioletred', 'papayawhip', 
            'peachpuff', 'peru', 'plum', 'powderblue', 'rebeccapurple', 
            'rosybrown', 'royalblue', 'saddlebrown', 'seagreen', 'seashell', 
            'sienna', 'skyblue', 'slateblue', 'slategray', 'snow', 
            'springgreen', 'tan', 'teal', 'thistle', 'tomato', 'violet', 
            'wheat', 'whitesmoke', 'yellowgreen'
        ]
 
        self.color_var = tk.StringVar()
        self.color_dropdown = tk.OptionMenu(self, self.color_var, *color_options)
        self.color_dropdown.grid(row=2, column=5, columnspan=2)

        # Create a button for applying the selected color to the selected value
        self.apply_color_button = tk.Button(self, text="Apply Color")
        self.apply_color_button.grid(row=3, column=5, columnspan=2)

        # Function to update the visibility and state of the widgets
        def update_widgets(*args):
            if self.categorical_color_map_var.get():
                self.unique_values_treeview.state(('!disabled',))
                self.color_dropdown.config(state=tk.NORMAL)
                self.apply_color_button.config(state=tk.NORMAL)
            else:
                self.unique_values_treeview.state(('disabled',))
                self.color_dropdown.config(state=tk.DISABLED)
                self.apply_color_button.config(state=tk.DISABLED)

        # Call the update_widgets function whenever the check box is toggled
        self.categorical_color_map_var.trace('w', update_widgets)

        # Initialize the visibility and state of the widgets
        update_widgets()


    def on_generate_button_click(self):
        self.logic.color_ramp = self.logic.generate_and_display_color_palette(self.canvas, self.apply_button, self.hue_slider.get(), self.hue2_slider.get(), self.bins_slider.get(), self.ramp_type_var.get(), self.reverse_color_ramp_var)
        self.apply_button.config(state=tk.NORMAL)

    def on_reverse_color_ramp_changed(self):
        print("on_reverse_color_ramp_changed called")
        if self.logic.color_ramp is not None:
            print(f"color_ramp before: {self.logic.color_ramp}")
            if self.reverse_color_ramp_var.get():
                self.logic.color_ramp = reverse_color_ramp(self.logic.color_ramp)
            print(f"color_ramp after: {self.logic.color_ramp}")
            self.on_generate_button_click()
            print(f"color_ramp: {self.logic.color_ramp}")

    def on_apply_button_click(self):
        try:
            # Generate the styled GeoJSON data
            geojson_str = self.logic.get_styled_geojson(self.logic.working_object_a, self.logic.working_object_b, self.classification_method_var.get(), self.bins_slider.get(), self.logic.color_ramp)
            if geojson_str:
                # Convert the GeoJSON string to a GeoDataFrame
                gdf = gpd.GeoDataFrame.from_features(json.loads(geojson_str))

                # Create a colormap from the selected color ramp
                if self.logic.color_ramp:
                    colors = [self.logic.hsb_to_rgb(h, s, b) for h, s, b in self.logic.color_ramp]
                    cmap = ListedColormap(colors)
                else:
                    cmap = None

                # Plot the GeoDataFrame using the custom colormap
                if cmap:
                    gdf.plot(column='bin', cmap=cmap)
                else:
                    gdf.plot()
                    
                plt.show(block=False)
                
            self.apply_button_clicked = True
            self.enable_pass_data_button()
        except Exception as e:
            print(f"An error occurred in on_apply_button_click: {e}")

    def enable_pass_data_button(self):
        if self.apply_button_clicked and hasattr(self.app, 'folium_window') and self.app.folium_window is not None:
            self.pass_data_button.config(state=tk.NORMAL)

    def on_pass_data_button_click(self):
        # Generate the styled GeoJSON data
        geojson_str = self.logic.get_styled_geojson(self.logic.working_object_a, self.logic.working_object_b, self.classification_method_var.get(), self.bins_slider.get(), self.logic.color_ramp)
        if geojson_str:
            # Pass the data to the FoliumWindow instance
            if hasattr(self.app, 'folium_window'):
                if self.app.folium_window:
                    # Add a new layer to the folium window
                    self.app.folium_window.add_layer(geojson_str)

        # Enable the folium button in the main window
        if hasattr(self.app, 'folium_button'):
            self.app.folium_button.config(state=tk.NORMAL)

    def update_hue2_slider_state(self, hue2_label, hue2_slider, hue2_entry, ramp_type_var):
        if self.ramp_type_var.get() == 'diverging':
            self.hue2_label.grid(row=17, columnspan=2)
            self.hue2_slider.grid(row=18, columnspan=2)
            self.hue2_entry.grid(row=19, columnspan=2)
        else:
            self.hue2_label.grid_forget()
            self.hue2_slider.grid_forget()
            self.hue2_entry.grid_forget()

    @staticmethod
    def update_scale_from_entry(scale: Any, value: str) -> None:
        try:
            scale.set(int(value))
        except ValueError:
            pass
            
    def on_generate_categorical_color_map_button_click(self):
        try:
            # Get the selected property from the working_object_b variable
            selected_property = self.logic.working_object_b

            # Create an empty color map
            color_map = {}

            # Populate the color map with key-value pairs representing unique values and their corresponding colors
            for item_id in self.unique_values_treeview.get_children():
                item = self.unique_values_treeview.item(item_id)
                value = item['text']
                color = item['image']
                color_map[value] = color

            # Generate the styled GeoJSON data
            geojson_str = self.logic.generate_categorical_color_map(self.logic.working_object_a, selected_property, color_map)           
            if geojson_str:
                # Convert the GeoJSON string to a GeoDataFrame
                gdf = gpd.GeoDataFrame.from_features(json.loads(geojson_str))

                # Plot the GeoDataFrame
                gdf.plot()
                
                plt.show(block=False)
                
            self.apply_button_clicked = True
            self.enable_pass_data_button()
        except Exception as e:
            print(f"An error occurred in on_generate_categorical_color_map_button_click: {e}")
            
