import tkinter as tk
from tkinter.filedialog import askdirectory
import os
import csv
from TableWidgets import PatternTableWidget
from TableWidgets import ParameterTableWidget


class SaveAndLoadWidget(tk.Frame):
    def __init__(self, parent, row, column, pattern_table: PatternTableWidget,
                 velocity_table: ParameterTableWidget, position_table: ParameterTableWidget):
        super().__init__(parent)

        # Positioning in parent
        self.config(padx=5, pady=5)
        self.grid(row=row, column=column, columnspan=3, sticky='nsew')
        parent.columnconfigure(column, weight=1)

        # Non widget member variables
        self.storage_folder_directory = tk.StringVar()
        self.storage_folder_directory.set(os.getcwd())
        self.pattern_table = pattern_table
        self.velocity_table = velocity_table
        self.position_table = position_table

        # Widget member variables
        self.save_button = tk.Button(master=self,
                                     height=1,
                                     text="Save tables",
                                     command=self.save_table_data,
                                     padx=5)

        self.load_button = tk.Button(master=self,
                                     height=1,
                                     text="Load tables",
                                     command=self.load_table_data,
                                     padx=5)
        self.select_storage_folder_button = tk.Button(master=self,
                                                      height=1,
                                                      text="Select storage folder",
                                                      command=self.select_directory,
                                                      padx=5)
        self.storage_folder_indicator_label = tk.Label(master=self,
                                                       text='Storage directory:')
        self.storage_folder_label = tk.Label(master=self,
                                             textvariable=self.storage_folder_directory)

        # Widget positioning
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.load_button.pack(side=tk.LEFT, padx=5)
        self.select_storage_folder_button.pack(side=tk.LEFT, padx=5)
        self.storage_folder_indicator_label.pack(side=tk.LEFT, padx=5)
        self.storage_folder_label.pack(side=tk.LEFT, padx=5)

    def save_table_data(self):
        with open(self.storage_folder_directory.get() + '/pattern_file.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.pattern_table.get_data())

        with open(self.storage_folder_directory.get() + '/velocity_file.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.velocity_table.get_data())

        with open(self.storage_folder_directory.get() + '/position_file.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.position_table.get_data())

    def load_table_data(self):
        with open(self.storage_folder_directory.get() + '/pattern_file.csv', mode='r') as file:
            reader = csv.reader(file)
            self.pattern_table.set_data(list(reader))

        with open(self.storage_folder_directory.get() + '/velocity_file.csv', mode='r') as file:
            reader = csv.reader(file)
            self.velocity_table.set_data(list(reader))

        with open(self.storage_folder_directory.get() + '/position_file.csv', mode='r') as file:
            reader = csv.reader(file)
            self.position_table.set_data(list(reader))

    def select_directory(self):
        directory = askdirectory(initialdir=self.storage_folder_directory.get())
        if directory:
            self.storage_folder_directory.set(directory)
