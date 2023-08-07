import numpy as np
import tkinter as tk
from file_utils import add_files, on_select, set_working_object_a, set_working_object_b, file_path_mapping
from color_window import ColorWindowLogic, ColorWindowGUI
from folium_window import FoliumWindowLogic, FoliumWindowGUI


class AppLogic:
    def __init__(self):
        self.working_object_a = None
        self.working_object_b = None
        self.selected_property = None

    def add_files(self, listbox):
        add_files(listbox)

    def on_select(self, listbox, property_listbox):
        on_select(listbox, property_listbox)

    def set_working_object_a(self, listbox, text_widget_a):
        self.working_object_a = set_working_object_a(listbox, text_widget_a)

    def set_working_object_b(self, property_listbox, text_widget_b):
        self.working_object_b = set_working_object_b(property_listbox, text_widget_b)
        
    def reset_working_object_a(self):
        self.working_object_a = None

    def reset_working_object_b(self):
        self.working_object_b = None
        
    def delete_file(self, listbox, property_listbox):
        selected_items = listbox.curselection()
        for item in selected_items:
            value = listbox.get(item)
            # look up the full file path based on the alias
            file_path = file_path_mapping[value]
            # delete the item from the listbox
            listbox.delete(item)
            # remove the file path from memory
            del file_path_mapping[value]
            # check if the deleted file was set as the working object
            if self.working_object_a is not None and file_path == self.working_object_a.source_file:
                # reset the working object a
                self.working_object_a = None
        # clear the property listbox
        property_listbox.delete(0, tk.END)


class AppGUI:
    def __init__(self, logic):
        self.logic = logic
        self.root = tk.Tk()
        self.root.title('Foliumizer')
        self.root.geometry("705x630")

        # create and configure widgets
        # add titles above the listboxes
        self.file_label = tk.Label(self.root, text="Loaded Files")
        self.property_label = tk.Label(self.root, text="Properties of Selected File")

		# create the listboxes
        self.listbox = tk.Listbox(self.root, height=15, width=40, exportselection=False)
        self.property_listbox = tk.Listbox(self.root, height=15, width=40, exportselection=False)

        # create the scrollbars for the listboxes
        self.listbox_v_scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox_h_scrollbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.listbox.xview)
        self.property_listbox_v_scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.property_listbox.yview)
        self.property_listbox_h_scrollbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.property_listbox.xview)

        # configure the listboxes to use the scrollbars
        self.listbox.config(yscrollcommand=self.listbox_v_scrollbar.set, xscrollcommand=self.listbox_h_scrollbar.set)
        self.property_listbox.config(yscrollcommand=self.property_listbox_v_scrollbar.set, xscrollcommand=self.property_listbox_h_scrollbar.set)

		# create the buttons
        self.add_button = tk.Button(self.root, text="Add Files", command=self.add_files_command)
        self.set_button = tk.Button(self.root, text="Set Spatial Data of Working Object", command=self.set_working_object_a_command)
        self.set_button_b = tk.Button(self.root, text="Set Active Property of Working Object", command=self.set_working_object_b_command)
        self.generate_color_button = tk.Button(self.root, text="Generate Color Palette", command=self.open_color_window)
        self.folium_button = tk.Button(self.root, text="Open Folium Window", command=self.open_folium_window)
        self.delete_button = tk.Button(self.root, text="Delete File", command=self.delete_file_command)
        self.reset_a_button = tk.Button(self.root, text="Reset Working Object A", command=self.reset_working_object_a_command)
        self.reset_b_button = tk.Button(self.root, text="Reset Working Object B", command=self.reset_working_object_b_command)

		# create the text widgets
        self.text_widget_a = tk.Text(self.root, height=5, width=40)
        self.text_widget_b = tk.Text(self.root, height=5, width=40)

        # create the scrollbars for the text widgets
        self.text_widget_a_v_scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.text_widget_a.yview)
        self.text_widget_a_h_scrollbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.text_widget_a.xview)
        self.text_widget_b_v_scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.text_widget_b.yview)
        self.text_widget_b_h_scrollbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.text_widget_b.xview)

        # configure the text widgets to use the scrollbars
        self.text_widget_a.config(yscrollcommand=self.text_widget_a_v_scrollbar.set, xscrollcommand=self.text_widget_a_h_scrollbar.set, wrap=tk.NONE)  # disable line wrapping to enable horizontal scrolling
        self.text_widget_b.config(yscrollcommand=self.text_widget_b_v_scrollbar.set, xscrollcommand=self.text_widget_b_h_scrollbar.set, wrap=tk.NONE)  # disable line wrapping to enable horizontal scrolling

		# bind events to the listbox
        self.listbox.bind("<<ListboxSelect>>", self.on_select_command)

		# use the grid geometry manager to position the widgets in the window
        self.add_button.grid(row=0, column=0, columnspan=6, padx=5, pady=5)
        self.delete_button.grid(row=1, column=0, columnspan=6, padx=5, pady=5)
        self.file_label.grid(row=2, column=1, columnspan=1, padx=5, pady=5) 
        self.listbox.grid(row=3, column=1, columnspan=1, padx=5, pady=5)
        self.listbox_v_scrollbar.grid(row=3, column=0)  
        self.listbox_h_scrollbar.grid(row=4, column=1)  
        self.set_button.grid(row=5, column=1, columnspan=1, padx=5, pady=5)
        self.reset_a_button.grid(row=6, column=1, columnspan=1, padx=5, pady=5)
        self.property_label.grid(row=2, column=4, columnspan=1, padx=5, pady=5)
        self.property_listbox.grid(row=3, column=4, columnspan=1, padx=5, pady=5)
        self.property_listbox_v_scrollbar.grid(row=3, column=5) 
        self.property_listbox_h_scrollbar.grid(row=4, column=4) 
        self.set_button_b.grid(row=5, column=4, columnspan=1, padx=5, pady=5)
        self.reset_b_button.grid(row=6, column=4, columnspan=1, padx=5, pady=5)
        self.text_widget_a.grid(row=7, column=1, columnspan=1, padx=5, pady=5)
        self.text_widget_a_v_scrollbar.grid(row=7, column=0)
        self.text_widget_a_h_scrollbar.grid(row=8, column=1)
        self.text_widget_b.grid(row=7, column=4, padx=5, pady=5)
        self.text_widget_b_v_scrollbar.grid(row=7, column=5)
        self.text_widget_b_h_scrollbar.grid(row=8, column=4)
        self.generate_color_button.grid(row=9, column=0, columnspan=6, padx=5, pady=5)
        self.folium_button.grid(row=10, column=0, columnspan=6, padx=5, pady=5)
 

    def add_files_command(self):
        self.logic.add_files(self.listbox)

    def on_select_command(self, event):
        self.logic.on_select(self.listbox, self.property_listbox)

    def set_working_object_a_command(self):
        self.logic.set_working_object_a(self.listbox, self.text_widget_a)

    def set_working_object_b_command(self):
        self.logic.set_working_object_b(self.property_listbox, self.text_widget_b)

    def reset_working_object_a_command(self):
        self.logic.reset_working_object_a()
        # delete the existing content of the text widget
        self.text_widget_a.delete("1.0", tk.END)
        # insert the new message into the text widget
        self.text_widget_a.insert(tk.END, "Working object A has been reset\n")

    def reset_working_object_b_command(self):
        self.logic.reset_working_object_b()
        # delete the existing content of the text widget
        self.text_widget_b.delete("1.0", tk.END)
        # insert the new message into the text widget
        self.text_widget_b.insert(tk.END, "Working object B has been reset\n")

    def delete_file_command(self):
        self.logic.delete_file(self.listbox, self.property_listbox)

    def open_color_window(self):
        color_logic = ColorWindowLogic(working_object_a=self.logic.working_object_a, working_object_b=self.logic.working_object_b)
        color_window = ColorWindowGUI(master=self.root, app=self, logic=color_logic)
        self.color_window = color_window

        # Check the data type of the selected property field
        selected_property = self.logic.working_object_b
        selected_property_type = self.logic.working_object_a[selected_property].dtype.type
        print(f"Selected property type: {selected_property_type}")

        if selected_property_type in [int, float, np.int64, np.float64]:
            # Show choropleth frame and hide categorical frame
            color_window.choropleth_frame.pack()
            color_window.categorical_frame.pack_forget()
        elif selected_property_type in [str, bool, np.object_]:
            # Show categorical frame and hide choropleth frame
            color_window.categorical_frame.pack()
            color_window.choropleth_frame.pack_forget()
                
        if hasattr(self, 'folium_window'):
            x = self.folium_window.winfo_x()
            y = self.folium_window.winfo_y()
            width = self.folium_window.winfo_width()
            color_window.geometry(f"+{x + width + 10}+{y}")
        else:
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            color_window.geometry(f"+{x + 50}+{y + 50}")
        color_window.update_idletasks()
        self.color_window_x = color_window.winfo_x()
        self.color_window_y = color_window.winfo_y()
        self.color_window_width = color_window.winfo_width()
        self.color_window_height = color_window.winfo_height()
        color_window.mainloop()

    def open_folium_window(self):
        folium_logic = FoliumWindowLogic(working_object_a=self.logic.working_object_a, working_object_b=self.logic.working_object_b)
        folium_window = FoliumWindowGUI(master=self.root, logic=folium_logic)
        self.folium_window = folium_window
        if hasattr(self, 'color_window'):
            x = self.color_window.winfo_x()
            y = self.color_window.winfo_y()
            width = self.color_window.winfo_width()
            folium_window.geometry(f"+{x + width + 10}+{y}")
        else:
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            folium_window.geometry(f"+{x + 50}+{y + 50}")
        folium_window.update_idletasks()
        if hasattr(self, 'color_window'):
            self.color_window.enable_pass_data_button()

if __name__ == "__main__":
    logic = AppLogic()
    gui = AppGUI(logic)
    gui.root.mainloop()
	
