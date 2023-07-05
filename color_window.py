import tkinter as tk
from color_utils import generate_color_ramp, hsb_to_rgb, generate_and_display_color_palette, generate_styled_geojson, get_styled_geojson, set_color_ramp

class ColorWindow(tk.Toplevel):
    def __init__(self, master=None, working_object_a=None, working_object_b=None):
        super().__init__(master)
        self.working_object_a = working_object_a
        self.working_object_b = working_object_b
        self.create_widgets()

    def create_widgets(self):
    
        hue_label = tk.Label(self, text='Hue 1:')
        hue_label.pack()
        hue_slider = tk.Scale(self, from_=0, to=360, orient=tk.HORIZONTAL)
        hue_slider.set(0)
        hue_slider.pack()
        hue_entry_var = tk.StringVar(value='0')
        hue_entry_var.trace('w', lambda *args: update_scale_from_entry(hue_slider, hue_entry_var.get()))
        hue_entry = tk.Entry(self, textvariable=hue_entry_var)
        hue_entry.pack()

        hue2_label = tk.Label(self, text='Hue 2:')
        hue2_slider = tk.Scale(self, from_=0, to=360, orient=tk.HORIZONTAL)
        hue2_slider.set(0)
        hue2_entry_var = tk.StringVar(value='0')
        hue2_entry_var.trace('w', lambda *args: update_scale_from_entry(hue2_slider, hue2_entry_var.get()))
        hue2_entry = tk.Entry(self, textvariable=hue2_entry_var)

        bins_label = tk.Label(self, text='Number of bins:')
        bins_label.pack()
        bins_slider = tk.Scale(self, from_=2, to=20, orient=tk.HORIZONTAL)
        bins_slider.set(2)
        bins_slider.pack()

        ramp_type_label = tk.Label(self,text='Color ramp type:')
        ramp_type_label.pack()
        ramp_type_var = tk.StringVar(value='sequential')
        sequential_ramp_button = tk.Radiobutton(self,text='Sequential',variable=ramp_type_var,value='sequential', command=lambda: self.update_hue2_slider_state(hue2_label, hue2_slider, hue2_entry, ramp_type_var.get()))
        sequential_ramp_button.pack()
        diverging_ramp_button = tk.Radiobutton(self,text='Diverging',variable=ramp_type_var,value='diverging', command=lambda: self.update_hue2_slider_state(hue2_label, hue2_slider, hue2_entry, ramp_type_var.get()))
        diverging_ramp_button.pack()

        self.update_hue2_slider_state(hue2_label, hue2_slider, hue2_entry, ramp_type_var.get())
        
        canvas = tk.Canvas(self, width=200, height=50)
        canvas.pack()
        
        classification_method_label = tk.Label(self, text='Classification method:')
        classification_method_label.pack()
        
        classification_method_var = tk.StringVar(value='quantiles')
        classification_method_options = ['quantiles', 'equal_interval', 'standard_deviation']
        classification_method_menu = tk.OptionMenu(self, classification_method_var, *classification_method_options)
        classification_method_menu.pack()

        color_ramp = None

        generate_button = tk.Button(self, text='Generate Color Palette', command=on_generate_button_click)
        generate_button.pack()

        apply_button = tk.Button(self, text='Preview Color Palette', state=tk.DISABLED, command=on_apply_button_click)
        apply_button.pack()

        pass_data_button = tk.Button(self, text='Add this Layer to Folium Map', command=self.on_pass_data_button_click)
        pass_data_button.pack()
        
        def get_hue1(self):
            return self.hue_slider.get()

        def get_hue2(self):
            return self.hue2_slider.get()

        def get_bins(self):
            return self.bins_slider.get()

        def get_ramp_type(self):
            return self.ramp_type_var.get()

        def generate_color_palette(parent, on_apply_callback, working_object_a, working_object_b):
            color_window = tk.Toplevel(parent)
            color_window.title('Generate Color Palette')

        def on_generate_button_click():
            nonlocal color_ramp
            color_ramp = generate_and_display_color_palette(canvas, apply_button, hue_slider.get(), hue2_slider.get(), bins_slider.get(), ramp_type_var.get())
            apply_button.config(state=tk.NORMAL)

        generate_button = tk.Button(self, text='Generate Color Palette', command=on_generate_button_click)
        generate_button.pack()

        def on_apply_button_click(self):
            # Generate the styled GeoJSON data
            self.styled_geojson = generate_styled_geojson(self.color_ramp, self.bins_slider.get(), self.classification_method_var.get(), self.working_object_a, self.working_object_b)

        apply_button = tk.Button(self, text='Preview Color Palette', state=tk.DISABLED, command=on_apply_button_click)
        apply_button.pack()

        def on_pass_data_button_click(self):
            # Pass the data to the FoliumWindow instance
            if self.folium_window and self.styled_geojson:
                self.folium_window.add_layer(self.styled_geojson)

    def update_hue2_slider_state(self, hue2_label, hue2_slider, hue2_entry, ramp_type):
        if ramp_type == 'diverging':
            hue2_label.pack()
            hue2_slider.pack()
            hue2_entry.pack()
        else:
            hue2_label.pack_forget()
            hue2_slider.pack_forget()
            hue2_entry.pack_forget()

    def update_scale_from_entry(scale, value):
        try:
            scale.set(int(value))
        except ValueError:
            pass
        