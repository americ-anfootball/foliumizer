import tkinter as tk
from tkinter import filedialog
import geopandas as gpd
import json
from file_utils import import_data, read_file, open_file_dialog, add_files, on_select, load_vector_data, set_working_object_a, set_working_object_b
from color_window import ColorWindow
from color_utils import generate_color_ramp, generate_and_display_color_palette, generate_styled_geojson
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import ListedColormap
from branca.colormap import LinearColormap
import folium
import json
import numpy as np
import webbrowser
from folium_window import FoliumWindow
#import threading
#from multiprocessing import Process

class App:

    #def on_close(self):
        ## Wait for all threads to finish
        #for thread in threading.enumerate():
            #if thread is not threading.current_thread():
                #thread.join()
        
        ## Terminate all processes
        #print(f"Terminating {len(self.my_processes)} processes")
        #for i, process in enumerate(self.my_processes):
            #process.terminate()
            #print(f"Terminated {i+1} out of {len(self.my_processes)} processes")
        
        ## Destroy the root window
        #self.root.destroy()
    
    def add_files_command(self):
        add_files(self.listbox)
        
    def on_select_command(self, event):
        on_select(self.listbox, self.property_listbox)
        
    def set_working_object_a_command(self):
        self.working_object_a = set_working_object_a(self.listbox, self.text_widget_a)

    def set_working_object_b_command(self):
        self.working_object_b = set_working_object_b(self.property_listbox, self.text_widget_b)

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Foliumizer')
        self.root.geometry("625x400")
        self.working_object_a = None
        self.working_object_b = None
        self.selected_property = None
        self.color_ramp = None
        self.bins = 5

        # add titles above the listboxes
        self.file_label = tk.Label(self.root, text="Files")
        self.property_label = tk.Label(self.root, text="Properties")

        # set the exportselection option of the listbox to False
        self.listbox = tk.Listbox(self.root, exportselection=False)

        self.add_button = tk.Button(self.root, text="Add Files", command=self.add_files_command)

        self.listbox.bind("<<ListboxSelect>>", self.on_select_command)

        # set the exportselection option of the property_listbox to False
        self.property_listbox = tk.Listbox(self.root, exportselection=False)

        self.set_button = tk.Button(self.root, text="Set Spatial Data of Working Object", command=self.set_working_object_a_command)
        self.set_button.grid(row=2, column=0)

        self.set_button_b = tk.Button(self.root, text="Set Property of Working Object", command=self.set_working_object_b_command)
        self.set_button_b.grid(row=2, column=1)

        # add two Text widgets to display the messages
        self.text_widget_a = tk.Text(self.root, height=5, width=40)
        self.text_widget_a.grid(row=3, column=0)

        self.text_widget_b = tk.Text(self.root, height=5, width=40)
        self.text_widget_b.grid(row=3, column=1)

        # add a button to generate a color palette
        self.generate_color_button = tk.Button(self.root, text="Generate Color Palette", command=self.open_color_window)

        # use the grid geometry manager to position the widgets in the window
        self.file_label.grid(row=0, column=0)
        self.property_label.grid(row=0, column=1)
        self.listbox.grid(row=1, column=0, padx=5)
        self.property_listbox.grid(row=1, column=1, padx=5)
        self.add_button.grid(row=2, column=0, columnspan=2)
        self.set_button.grid(row=2, column=0, padx=5)
        self.set_button_b.grid(row=2, column=1, padx=5)
        self.generate_color_button.grid(row=4, column=0, columnspan=2)

        # Create a Button widget for opening the folium window
        self.folium_button = tk.Button(self.root, text="Open Folium Window", command=self.open_folium_window, state=tk.DISABLED)
        self.folium_button.grid(row=5, column=0, columnspan=2)

        ## Initialize the my_processes attribute with an empty list
        #self.my_processes = []

        ## add a protocol handler for the WM_DELETE_WINDOW event that calls the destroy method of the root window
        #self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.root.mainloop()
    
        # Create a color ramp listbox
        self.color_ramp_listbox = tk.Listbox(self.root, exportselection=False)
        self.color_ramp_listbox.grid(row=1, column=2)

        # Bind the <<ListboxSelect>> event of the color ramp listbox to the set_color_ramp method
        self.color_ramp_listbox.bind("<<ListboxSelect>>", lambda event: self.set_color_ramp())

    def create_process(self, target_function):
        # Create a new process
        new_process = Process(target=target_function)
        
        # Add the new process to the my_processes list
        self.my_processes.append(new_process)
        
        # Start the new process
        new_process.start()

    def open_color_window(self):
        # Get the selected column name from the second listbox
        selected_column_indices = self.property_listbox.curselection()
        if not selected_column_indices:
            message = "Please select a property"
            print(message)
            # insert message into text_widget instead of printing it to console
            self.text_widget_b.insert(tk.END, message + "\n")
            return
        selected_column_index = selected_column_indices[0]
        selected_column_name = self.property_listbox.get(selected_column_index)

        # Access the value of the listbox, text_widget_a, and property_listbox attributes from the self object
        listbox = self.listbox
        text_widget_a = self.text_widget_a
        text_widget_b = self.text_widget_b
        property_listbox = self.property_listbox

        # Call the set_working_object_a and set_working_object_b functions with the appropriate arguments
        working_object_a = set_working_object_a(listbox, text_widget_a)
        working_object_b = set_working_object_b(property_listbox, text_widget_b)

        # Create an instance of the ColorWindow class and pass the working objects as arguments
        color_window = ColorWindow(self.root, working_object_a, working_object_b)
  
    def open_folium_window(self):
        #Open a new folium window
        FoliumWindow(self.root, self, self.working_object_a, self.working_object_b)
        
app = App()
