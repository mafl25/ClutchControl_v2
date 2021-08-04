import tkinter as tk
from tkinter.filedialog import askdirectory
import serial.tools.list_ports as ports
import tksheet as table
import copy
import csv
import os


class CommWidget(tk.Frame):

    def __init__(self, parent, row, column, main_text):
        super().__init__(parent)

        # Positioning in parent
        self.config(padx=5, pady=5)
        self.grid(row=row, column=column, columnspan=3, sticky='nsew')
        parent.columnconfigure(column, weight=1)

        # Non widget member variables
        self.main_starting_text = main_text
        self.is_connected = False

        self.menu_main_text = tk.StringVar()
        self.menu_main_text.set(self.main_starting_text)

        self.status_text = tk.StringVar()
        self.status_text.set("Not connected")

        # Widget member variables
        port_list = ports.comports()
        self.drop_down_menu = tk.OptionMenu(self,
                                            self.menu_main_text,
                                            *port_list)
        self.drop_down_menu.config(width=50)

        self.status = tk.Label(master=self, width=35, textvariable=self.status_text)

        self.connect_button = tk.Button(master=self,
                                        height=1,
                                        text="Connect",
                                        command=self.connect_button_pressed,
                                        padx=5)

        self.update_button = tk.Button(master=self,
                                       height=1,
                                       text="Update port list",
                                       command=self.update_port_list,
                                       padx=5)

        # Widget positioning
        self.drop_down_menu.pack(side=tk.LEFT)
        self.status.pack(side=tk.RIGHT)
        self.connect_button.pack(side=tk.RIGHT, padx=5)
        self.update_button.pack(side=tk.RIGHT, padx=5)

    def update_port_list(self):
        self.drop_down_menu['menu'].delete(0, 'end')
        port_list = ports.comports()
        if len(port_list) == 0:
            self.status_text.set("No COM ports detected")
        else:
            for port in port_list:
                self.drop_down_menu['menu'].add_command(label=port,
                                                        command=lambda value=port: self.menu_main_text.set(value))

    def has_a_port_been_selected(self):
        return self.menu_main_text.get() != self.main_starting_text

    def connect_button_pressed(self):
        if self.is_connected is False:
            if self.has_a_port_been_selected() is True:
                self.is_connected = True
                self.status_text.set('Connected')
            else:
                self.status_text.set('Port not selected')
        elif self.is_connected is True:
            self.is_connected = False
            self.status_text.set('Not connected')


class PatternTableWidget(tk.Frame):
    def __init__(self, parent, row, column):
        super().__init__(parent)

        # Positioning in parent
        self.config(padx=5, pady=5)
        self.grid(row=row, column=column, columnspan=1, sticky='nsew')
        parent.columnconfigure(column, weight=1)

        # Widget variables
        self.main_label = tk.Label(self, text="Pattern table", pady=10)

        number_of_columns = 3
        table_data = [[''] * number_of_columns]
        self.table = table.Sheet(self)
        self.table.set_sheet_data(table_data)
        self.table.enable_bindings(("single_select",
                                    "row_select",
                                    "column_width_resize",
                                    "arrowkeys",
                                    "right_click_popup_menu",
                                    "rc_select",
                                    "rc_insert_row",
                                    "rc_delete_row",
                                    "copy",
                                    "cut",
                                    "paste",
                                    "delete",
                                    "undo",
                                    "edit_cell"))
        self.table.hide(canvas='x_scrollbar')

        # Widget positioning
        self.main_label.grid(row=0, column=0)
        self.table.grid(row=1, column=0, padx=5)

    def get_data(self):
        original_data = copy.deepcopy(self.table.get_sheet_data())
        sanitized_data = []
        try:
            for row in original_data:
                new_row = []
                for index, element in enumerate(row):
                    try:
                        new_row.append(float(element))
                    except ValueError:
                        if (element == 'VELOCITY' and index == 1) or (element == 'TIME' and index == 0):
                            new_row.append(element)
                        else:
                            raise Exception('Incorrect input')
                sanitized_data.append(new_row)
            return sanitized_data
        except Exception as error_message:
            print(error_message)
            return None

    def set_data(self, data):
        self.table.set_sheet_data(copy.deepcopy(data))


class ParameterTableWidget(tk.Frame):
    def __init__(self, parent, row, column, title):
        super().__init__(parent)

        # Positioning in parent
        self.config(padx=5, pady=5)
        self.grid(row=row, column=column, columnspan=1, sticky='nsew')
        parent.columnconfigure(column, weight=1)

        # Non widget member variables
        self.randomize_variable = tk.BooleanVar()
        self.randomize_variable.set(False)

        # Widget member variables
        self.main_label = tk.Label(self, text=title, pady=10)

        self.randomize_checkbutton = tk.Checkbutton(self,
                                                    text="Randomize",
                                                    variable=self.randomize_variable)

        table_data = [['']]
        self.table = table.Sheet(self)
        self.table.set_sheet_data(table_data)
        self.table.enable_bindings(("single_select",
                                    "row_select",
                                    "column_width_resize",
                                    "arrowkeys",
                                    "right_click_popup_menu",
                                    "rc_select",
                                    "rc_insert_row",
                                    "rc_delete_row",
                                    "copy",
                                    "cut",
                                    "paste",
                                    "delete",
                                    "undo",
                                    "edit_cell"))

        # Widget positioning
        self.main_label.grid(row=0, column=0, sticky='w')
        self.randomize_checkbutton.grid(row=0, column=1, sticky='e')
        self.table.grid(row=1, column=0, columnspan=2, padx=5)

    def get_data(self):
        raw_data = copy.deepcopy(self.table.get_sheet_data())
        return raw_data

    def set_data(self, data):
        self.table.set_sheet_data(copy.deepcopy(data))


class SaveAndLoadWidget(tk.Frame):
    def __init__(self, parent, row, column):
        super().__init__(parent)

        # Positioning in parent
        self.parent = parent
        self.config(padx=5, pady=5)
        self.grid(row=row, column=column, columnspan=3, sticky='nsew')
        self.parent.columnconfigure(column, weight=1)

        # Non widget member variables
        self.storage_folder_directory = tk.StringVar()
        self.storage_folder_directory.set(os.getcwd())

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
            writer.writerows(self.parent.pattern_table.get_data())

        with open(self.storage_folder_directory.get() + '/velocity_file.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.parent.velocity_table.get_data())

        with open(self.storage_folder_directory.get() + '/position_file.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.parent.position_table.get_data())

    def load_table_data(self):
        with open(self.storage_folder_directory.get() + '/pattern_file.csv', mode='r') as file:
            reader = csv.reader(file)
            self.parent.pattern_table.set_data(list(reader))

        with open(self.storage_folder_directory.get() + '/velocity_file.csv', mode='r') as file:
            reader = csv.reader(file)
            self.parent.velocity_table.set_data(list(reader))

        with open(self.storage_folder_directory.get() + '/position_file.csv', mode='r') as file:
            reader = csv.reader(file)
            self.parent.position_table.set_data(list(reader))

    def select_directory(self):
        directory = askdirectory(initialdir=self.storage_folder_directory.get())
        if directory:
            self.storage_folder_directory.set(directory)


def run_test_callback(control_board_port, torque_board_port, pattern_table, velocity_table, position_table):
    print(pattern_table.get_data())


class WindowGUI(tk.Tk):  # This is the base that will help use and add frames easily.

    def __init__(self, window_title, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tk.Tk.wm_title(self, window_title)

        self.control_board_port = CommWidget(parent=self,
                                             row=0,
                                             column=0,
                                             main_text='Control board COM port')
        self.ADC_board_port = CommWidget(parent=self,
                                         row=1,
                                         column=0,
                                         main_text='Torque measurement board COM port')

        self.pattern_table = PatternTableWidget(parent=self,
                                                row=2,
                                                column=0)

        self.velocity_table = ParameterTableWidget(parent=self,
                                                   row=2,
                                                   column=1,
                                                   title='Velocity table')

        self.position_table = ParameterTableWidget(parent=self,
                                                   row=2,
                                                   column=2,
                                                   title='Position table')

        self.save_and_load = SaveAndLoadWidget(parent=self,
                                               row=3,
                                               column=0)

        widgets = (self.control_board_port,
                   self.ADC_board_port,
                   self.pattern_table,
                   self.velocity_table,
                   self.position_table)

        self.run_test_button = tk.Button(master=self,
                                         height=1,
                                         text="Run test",
                                         command=lambda: run_test_callback(*widgets),
                                         padx=5)
        self.run_test_button.grid(row=4,
                                  column=2,
                                  padx=5,
                                  sticky='e')


if __name__ == "__main__":
    mainWindow = WindowGUI(window_title='Clutch control')
    mainWindow.state('zoomed')
    mainWindow.mainloop()
