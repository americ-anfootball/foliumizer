import geopandas as gpd
import json
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from color_utils import generate_color_ramp, hsb_to_rgb, generate_and_display_color_palette, set_color_ramp, get_styled_geojson, generate_styled_geojson, reverse_color_ramp, get_categorical_color_map, generate_categorical_color_map
from folium_window import FoliumWindowLogic, FoliumWindowGUI
from matplotlib.colors import ListedColormap
from tkinter.colorchooser import askcolor
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
        self.color_map = {}
        self.apply_button_clicked = False
        self.create_widgets()

    def create_widgets(self):
        try:
            # create a frame for all widgets associated with choropleth mapping
            self.choropleth_frame = tk.Frame(self)
            
            # create the hue label and slider
            self.hue_label = tk.Label(self.choropleth_frame, text='Hue 1:')
            self.hue_label.grid(row=0, columnspan=2)
            self.hue_slider = tk.Scale(self.choropleth_frame, from_=0, to=360, orient=tk.HORIZONTAL)
            self.hue_slider.set(0)
            self.hue_slider.grid(row=1, columnspan=2)

            # create the hue entry field
            self.hue_entry_var = tk.StringVar(value='0')
            self.hue_entry_var.trace('w', lambda *args: self.update_scale_from_entry(self.hue_slider, self.hue_entry_var.get()))
            self.hue_entry = tk.Entry(self.choropleth_frame, textvariable=self.hue_entry_var)
            self.hue_entry.grid(row=2, columnspan=2)

            # create the second hue label and slider
            self.hue2_label = tk.Label(self.choropleth_frame, text='Hue 2:')
            self.hue2_slider = tk.Scale(self.choropleth_frame, from_=0, to=360, orient=tk.HORIZONTAL)
            self.hue2_slider.set(0)
            self.hue2_entry_var = tk.StringVar(value='0')
            self.hue2_entry_var.trace('w', lambda *args: update_scale_from_entry(self.hue2_slider, self.hue2_entry_var.get()))
            self.hue2_entry = tk.Entry(self.choropleth_frame, textvariable=self.hue2_entry_var)

            # create the bins label and slider
            self.bins_label = tk.Label(self.choropleth_frame, text='Number of bins:')
            self.bins_label.grid(row=3,columnspan=2)
            self.bins_slider = tk.Scale(self.choropleth_frame, from_=2, to=20, orient=tk.HORIZONTAL)
            self.bins_slider.set(2)
            self.bins_slider.grid(row=4,columnspan=2)

            # create the ramp type label and radio buttons
            self.ramp_type_label = tk.Label(self.choropleth_frame,text='Color ramp type:')
            self.ramp_type_label.grid(row=5,columnspan=2)
            self.ramp_type_var = tk.StringVar(value='sequential')
            self.sequential_ramp_button = tk.Radiobutton(self.choropleth_frame,text='Sequential',variable=self.ramp_type_var,value='sequential', command=lambda: self.update_hue2_slider_state(self.hue2_label, self.hue2_slider, self.hue2_entry, self.ramp_type_var.get()))
            self.sequential_ramp_button.grid(row=6,columnspan=2)

            self.diverging_ramp_button = tk.Radiobutton(self.choropleth_frame,text='Diverging',variable=self.ramp_type_var,value='diverging', command=lambda: self.update_hue2_slider_state(self.hue2_label, self.hue2_slider, self.hue2_entry, self.ramp_type_var.get()))
            self.diverging_ramp_button.grid(row=7,columnspan=2)
            self.reverse_color_ramp_var = tk.BooleanVar()
            self.reverse_color_ramp_checkbox = tk.Checkbutton(self.choropleth_frame, text="Reverse Color Ramp", variable=self.reverse_color_ramp_var)
            self.reverse_color_ramp_checkbox.grid(row=8,columnspan=2)

            self.reverse_color_ramp_var.trace("w", lambda *args: self.choropleth_frame.on_reverse_color_ramp_changed())

            # update the state of the second hue slider
            self.update_hue2_slider_state(self.hue2_label, self.hue2_slider, self.hue2_entry, self.ramp_type_var.get())

            # create the canvas
            self.canvas = tk.Canvas(self.choropleth_frame, width=200, height=50)
            self.canvas.grid(row=9,columnspan=2)

            # create the classification method label and option menu
            self.classification_method_label = tk.Label(self.choropleth_frame, text='Classification method:')
            self.classification_method_label.grid(row=10,column=0)
            self.classification_method_var = tk.StringVar(value='quantiles')
            self.classification_method_options = ['quantiles', 'equal_interval', 'standard_deviation']
            self.classification_method_menu = tk.OptionMenu(self.choropleth_frame, self.classification_method_var, *self.classification_method_options)
            self.classification_method_menu.grid(row=10,column=1)

            color_ramp = None

            # create the generate and apply buttons
            self.generate_button = tk.Button(self.choropleth_frame, text='Generate Color Palette', command=self.on_generate_button_click)
            self.generate_button.grid(row=11,columnspan=2)

            self.apply_button = tk.Button(self.choropleth_frame, text='Preview Color Palette', state=tk.DISABLED, command=self.on_apply_button_click)
            self.apply_button.grid(row=12,columnspan=2)

            self.pass_data_button = tk.Button(self.choropleth_frame, text='Add this Layer to Folium Map', state=tk.DISABLED, command=self.on_pass_data_button_click)
            self.pass_data_button.grid(row=13,columnspan=2)
            
            # Pack the choropleth frame into the parent widget
            self.choropleth_frame.pack()

            # create a frame for all widgets associated with categorical mapping
            self.categorical_frame = tk.Frame(self)

            # Create a listbox to display the unique values
            self.unique_values_listbox = tk.Listbox(self.categorical_frame)
            self.unique_values_listbox.grid(row=0, column=1, columnspan=2)

            def populate_listbox():
                # Clear the listbox
                self.unique_values_listbox.delete(0, tk.END)

                # Get the unique values of the selected property field
                unique_values = self.logic.working_object_a[self.logic.working_object_b].unique()
                unique_values.sort()

                # Add the unique values to the listbox
                for value in unique_values:
                    self.unique_values_listbox.insert(tk.END, value)

            # Create a button to open the color picker
            self.color_picker_button = tk.Button(self.categorical_frame, text="Choose Color", command=self.on_color_picker_button_click)
            self.color_picker_button.grid(row=2, column=1, columnspan=2)

            # Create a canvas to display the selected color
            self.color_canvas = tk.Canvas(self.categorical_frame, width=40, height=20)
            self.color_canvas.grid(row=3, column=1, columnspan=2)
        
            # Create a button to apply the selected color
            self.apply_color_button = tk.Button(self.categorical_frame, text="Apply Color", command=self.on_apply_color_button_click)
            self.apply_color_button.grid(row=4, column=1, columnspan=2)
            
            # Create a button to generate the categorical color map
            self.generate_categorical_color_map_button = tk.Button(self.categorical_frame, text="Generate Categorical Color Map", command=self.on_generate_categorical_color_map_button_click)
            self.generate_categorical_color_map_button.grid(row=5, column=1, columnspan=2)
            
            # Create a button to pass the generated map to the Folium Window
            self.pass_categorical_map_button = tk.Button(self.categorical_frame, text="Add Result To Folium Window", command=self.on_pass_categorical_map_button_click)
            self.pass_categorical_map_button.grid(row=6, column=1, columnspan=2)
            
            # Populate the listbox
            populate_listbox()
            
            # Pack the categorical frame into the parent widget
            self.categorical_frame.pack()

            self.choropleth_frame.pack_forget()
            self.categorical_frame.pack_forget()
            
        except Exception as e:
            print(f"An error occurred while creating widgets: {e}")
            
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

    def on_color_picker_button_click(self):
        # Open the color picker dialog
        color_code = tk.colorchooser.askcolor()[1]

        # Update the canvas with the selected color
        self.color_canvas.delete("all")
        self.color_canvas.create_rectangle(0, 0, 40, 20, fill=color_code)

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
                    
                    # Add a new z layer to the folium window
                    self.app.folium_window.add_z_layer(geojson_str)

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
            
    def on_apply_color_button_click(self):
        selected_value = self.unique_values_listbox.get(tk.ANCHOR)
        print(f"Selected value: {selected_value}")

        selected_color = self.color_canvas.itemcget(self.color_canvas.find_all()[0], "fill")
        print(f"Selected color: {selected_color}")

        self.color_map[selected_value] = selected_color
        print(f"Updated color_map: {self.color_map}")
            
    def on_generate_categorical_color_map_button_click(self):
        try:
            # Get the selected property from the working_object_b variable
            selected_property = self.logic.working_object_b

            # Get the color map from the color_map attribute
            color_map = self.color_map

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

    def on_pass_categorical_map_button_click(self):
        # Call the get_categorical_color_map function to generate a geojson string
        geojson_str = self.logic.get_categorical_color_map(self.logic.working_object_a, self.logic.working_object_b, self.color_map)

        if geojson_str:
            # Check if the folium_window attribute exists and is not None
            if hasattr(self.app, 'folium_window') and self.app.folium_window:
                # Call the add_layer method of the folium_window object
                self.app.folium_window.add_layer(geojson_str)
                
                # Add a new z layer to the folium window
                self.app.folium_window.add_z_layer(geojson_str)

        # Enable the folium button in the main window
        if hasattr(self.app, 'folium_button'):
            self.app.folium_button.config(state=tk.NORMAL)
