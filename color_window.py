import geopandas as gpd
import json
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from color_utils import generate_color_ramp, hsb_to_rgb, generate_and_display_color_palette, set_color_ramp, get_styled_geojson, generate_styled_geojson
from folium_window import FoliumWindowLogic, FoliumWindowGUI
from matplotlib.colors import ListedColormap
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

    def generate_and_display_color_palette(self, canvas: Any, apply_button: Any, hue1: int, hue2: int, bins: int, ramp_type: str) -> List[Tuple[int, int, int]]:
        return generate_and_display_color_palette(canvas, apply_button, hue1, hue2, bins, ramp_type)

    def set_color_ramp(self, color_ramp_listbox: Any, text_widget_c: Any) -> str:
        return set_color_ramp(color_ramp_listbox, text_widget_c)

    def get_styled_geojson(self, geojson_data: Any, selected_property: str, classification_method: str, bins: int, color_ramp: List[Tuple[int, int, int]]) -> str:
        return get_styled_geojson(geojson_data, selected_property, classification_method, bins, color_ramp)

    def generate_styled_geojson(self, color_ramp: List[Tuple[int, int, int]], bins: int, classification_method: str) -> str:
        return generate_styled_geojson(color_ramp, bins, classification_method)


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
            self.hue_label.pack()
            self.hue_slider = tk.Scale(self, from_=0, to=360, orient=tk.HORIZONTAL)
            self.hue_slider.set(0)
            self.hue_slider.pack()

            # create the hue entry field
            self.hue_entry_var = tk.StringVar(value='0')
            self.hue_entry_var.trace('w', lambda *args: self.update_scale_from_entry(self.hue_slider, self.hue_entry_var.get()))
            self.hue_entry = tk.Entry(self, textvariable=self.hue_entry_var)
            self.hue_entry.pack()

            # create the second hue label and slider
            self.hue2_label = tk.Label(self, text='Hue 2:')
            self.hue2_slider = tk.Scale(self, from_=0, to=360, orient=tk.HORIZONTAL)
            self.hue2_slider.set(0)
            self.hue2_entry_var = tk.StringVar(value='0')
            self.hue2_entry_var.trace('w', lambda *args: update_scale_from_entry(self.hue2_slider, self.hue2_entry_var.get()))
            self.hue2_entry = tk.Entry(self, textvariable=self.hue2_entry_var)

            # create the bins label and slider
            self.bins_label = tk.Label(self, text='Number of bins:')
            self.bins_label.pack()
            self.bins_slider = tk.Scale(self, from_=2, to=20, orient=tk.HORIZONTAL)
            self.bins_slider.set(2)
            self.bins_slider.pack()

            # create the ramp type label and radio buttons
            self.ramp_type_label = tk.Label(self,text='Color ramp type:')
            self.ramp_type_label.pack()
            self.ramp_type_var = tk.StringVar(value='sequential')
            self.sequential_ramp_button = tk.Radiobutton(self,text='Sequential',variable=self.ramp_type_var,value='sequential', command=lambda: self.update_hue2_slider_state(self.hue2_label, self.hue2_slider, self.hue2_entry, self.ramp_type_var.get()))
            self.sequential_ramp_button.pack()
            self.diverging_ramp_button = tk.Radiobutton(self,text='Diverging',variable=self.ramp_type_var,value='diverging', command=lambda: self.update_hue2_slider_state(self.hue2_label, self.hue2_slider, self.hue2_entry, self.ramp_type_var.get()))
            self.diverging_ramp_button.pack()

            # update the state of the second hue slider
            self.update_hue2_slider_state(self.hue2_label, self.hue2_slider, self.hue2_entry, self.ramp_type_var.get())

            # create the canvas
            self.canvas = tk.Canvas(self, width=200, height=50)
            self.canvas.pack()

            # create the classification method label and option menu
            self.classification_method_label = tk.Label(self, text='Classification method:')
            self.classification_method_label.pack()
            self.classification_method_var = tk.StringVar(value='quantiles')
            self.classification_method_options = ['quantiles', 'equal_interval', 'standard_deviation']
            self.classification_method_menu = tk.OptionMenu(self, self.classification_method_var, *self.classification_method_options)
            self.classification_method_menu.pack()

            color_ramp = None

            # create the generate and apply buttons
            self.generate_button = tk.Button(self, text='Generate Color Palette', command=self.on_generate_button_click)
            self.generate_button.pack()
            
            self.apply_button = tk.Button(self, text='Preview Color Palette', state=tk.DISABLED, command=self.on_apply_button_click)
            self.apply_button.pack()

            self.pass_data_button = tk.Button(self, text='Add this Layer to Folium Map', state=tk.DISABLED, command=self.on_pass_data_button_click)
            self.pass_data_button.pack()
        except Exception as e:
            print(f"An error occurred while creating widgets: {e}")

    def on_generate_button_click(self):
        self.logic.color_ramp = self.logic.generate_and_display_color_palette(self.canvas, self.apply_button, self.hue_slider.get(), self.hue2_slider.get(), self.bins_slider.get(), self.ramp_type_var.get())
        self.apply_button.config(state=tk.NORMAL)

    def on_apply_button_click(self):
        print("on_apply_button_click called")
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
            print(f"apply_button_clicked set to {self.apply_button_clicked}")
        except Exception as e:
            print(f"An error occurred in on_apply_button_click: {e}")
        print("on_apply_button_click finished")

    def enable_pass_data_button(self):
        print("enable_pass_data_button called")
        print(f"apply_button_clicked: {self.apply_button_clicked}")
        if self.apply_button_clicked and hasattr(self.app, 'folium_window') and self.app.folium_window is not None:
            print("enabling pass_data_button")
            self.pass_data_button.config(state=tk.NORMAL)
        else:
            print("conditions for enabling pass_data_button not met")

    def on_pass_data_button_click(self):
        #print("on_pass_data_button_click called")
        #print(f"self.app: {self.app}")
        # Generate the styled GeoJSON data
        geojson_str = self.logic.get_styled_geojson(self.logic.working_object_a, self.logic.working_object_b, self.classification_method_var.get(), self.bins_slider.get(), self.logic.color_ramp)
        if geojson_str:
            # Pass the data to the FoliumWindow instance
            #print(f"hasattr(self.app, 'folium_window'): {hasattr(self.app, 'folium_window')}")
            if hasattr(self.app, 'folium_window'):
                #print(f"self.app.folium_window: {self.app.folium_window}")
                if self.app.folium_window:
                    #print("passing data to folium window")
                    # Add a new layer to the folium window
                    self.app.folium_window.add_layer(geojson_str)

        # Enable the folium button in the main window
        if hasattr(self.app, 'folium_button'):
            #print("enabling folium_button")
            self.app.folium_button.config(state=tk.NORMAL)

    def update_hue2_slider_state(self, hue2_label, hue2_slider, hue2_entry, ramp_type_var):
        if self.ramp_type_var.get() == 'diverging':
            self.hue2_label.pack()
            self.hue2_slider.pack()
            self.hue2_entry.pack()
        else:
            self.hue2_label.pack_forget()
            self.hue2_slider.pack_forget()
            self.hue2_entry.pack_forget()

    @staticmethod
    def update_scale_from_entry(scale: Any, value: str) -> None:
        try:
            scale.set(int(value))
        except ValueError:
            pass
