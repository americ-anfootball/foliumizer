import tkinter as tk
from file_utils import add_files, on_select, set_working_object_a, set_working_object_b
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


class AppGUI:
    def __init__(self, logic):
        self.logic = logic
        self.root = tk.Tk()
        self.root.title('Foliumizer')
        self.root.geometry("675x525")

        # create and configure widgets
        # add titles above the listboxes
        self.file_label = tk.Label(self.root, text="Loaded Files")
        self.property_label = tk.Label(self.root, text="Properties of Selected File")

		# create the listboxes
        self.listbox = tk.Listbox(self.root, height=15, width=40, exportselection=False)
        self.property_listbox = tk.Listbox(self.root, height=15, width=40, exportselection=False)

		# create the buttons
        self.add_button = tk.Button(self.root, text="Add Files", command=self.add_files_command)
        self.set_button = tk.Button(self.root, text="Set Spatial Data of Working Object", command=self.set_working_object_a_command)
        self.set_button_b = tk.Button(self.root, text="Set Active Property of Working Object", command=self.set_working_object_b_command)
        self.generate_color_button = tk.Button(self.root, text="Generate Color Palette", command=self.open_color_window)
        self.folium_button = tk.Button(self.root, text="Open Folium Window", command=self.open_folium_window, state=tk.DISABLED)

		# create the text widgets
        self.text_widget_a = tk.Text(self.root, height=5, width=40)
        self.text_widget_b = tk.Text(self.root, height=5, width=40)

		# bind events to the listbox
        self.listbox.bind("<<ListboxSelect>>", self.on_select_command)

		# use the grid geometry manager to position the widgets in the window
        self.add_button.grid(row=0, column=0, columnspan=6, padx=5, pady=5)
        self.file_label.grid(row=2, column=1, columnspan=1, padx=5, pady=5) 
        self.listbox.grid(row=3, column=1, columnspan=1, padx=5, pady=5)
        self.set_button.grid(row=4, column=1, columnspan=1, padx=5, pady=5)
        self.property_label.grid(row=2, column=4, columnspan=1, padx=5, pady=5)
        self.property_listbox.grid(row=3, column=4, columnspan=1, padx=5, pady=5)
        self.set_button_b.grid(row=4, column=4, columnspan=1, padx=5, pady=5)
        self.text_widget_a.grid(row=5, column=1, columnspan=1, padx=5, pady=5)
        self.text_widget_b.grid(row=5, column=4, columnspan=1, padx=5, pady=5)
        self.generate_color_button.grid(row=6, column=0, columnspan=6, padx=5, pady=5)
        self.folium_button.grid(row=7, column=0, columnspan=6)

    def add_files_command(self):
        self.logic.add_files(self.listbox)

    def on_select_command(self, event):
        self.logic.on_select(self.listbox, self.property_listbox)

    def set_working_object_a_command(self):
        self.logic.set_working_object_a(self.listbox, self.text_widget_a)

    def set_working_object_b_command(self):
        self.logic.set_working_object_b(self.property_listbox, self.text_widget_b)

    def open_color_window(self):
        color_logic = ColorWindowLogic(working_object_a=self.logic.working_object_a, working_object_b=self.logic.working_object_b)
        color_window = ColorWindowGUI(master=self, logic=color_logic)
        color_window.mainloop()

    def open_folium_window(self):
        # Create an instance of the FoliumWindowLogic class
        folium_logic = FoliumWindowLogic(working_object_a=self.logic.working_object_a, working_object_b=self.logic.working_object_b)

        # Create an instance of the FoliumWindowGUI class
        folium_window = FoliumWindowGUI(master=self.root, logic=folium_logic)

        # Store a reference to the folium window as an instance attribute
        self.folium_window = folium_window


if __name__ == "__main__":
    logic = AppLogic()
    gui = AppGUI(logic)
    gui.root.mainloop()
