import tkinter as tk
from tkinter.filedialog import askdirectory
import serial.tools.list_ports as ports
import tksheet as table
import copy
import csv
import os
import time
import random


class CommWidget(tk.Frame):

    def __init__(self, parent, row, column, main_text, connected_callback=None, disconnected_callback=None):
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

        self.connected_callback = connected_callback
        self.disconnected_callback = disconnected_callback

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
                if self.connected_callback:
                    self.connected_callback()
            else:
                self.status_text.set('Port not selected')
        elif self.is_connected is True:
            self.is_connected = False
            self.status_text.set('Not connected')
            if self.disconnected_callback:
                self.disconnected_callback()


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
                            raise Exception(print('Input error in ' + self.main_label.cget("text")))
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
        original_data = copy.deepcopy(self.table.get_sheet_data())
        sanitized_data = []
        try:
            for row in original_data:
                new_row = []
                for index, element in enumerate(row):
                    new_row.append(float(element))
                sanitized_data.append(new_row)
            return sanitized_data
        except ValueError:
            print('Input error in ' + self.main_label.cget("text"))
            return None

    def set_data(self, data):
        self.table.set_sheet_data(copy.deepcopy(data))

    def should_randomize_data(self):
        return self.randomize_variable.get()


class SaveAndLoadWidget(tk.Frame):
    def __init__(self, parent, row, column, pattern_table, velocity_table, position_table):
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


class RunTestWidget(tk.Frame):
    def __init__(self, parent, row, column, pattern_table, velocity_table, position_table):
        super().__init__(parent)

        # Positioning in parent
        self.config(padx=5, pady=5)
        self.grid(row=row, column=column, columnspan=3, sticky='nsew')
        parent.columnconfigure(column, weight=1)

        # Non widget member variables
        self.run_test_status = tk.StringVar()
        self.run_test_status.set('No test running.')
        self.pattern_table = pattern_table
        self.velocity_table = velocity_table
        self.position_table = position_table
        self.waiting_for_position = False

        # Widget member variables
        self.run_test_button = tk.Button(master=self,
                                         height=1,
                                         text="Run test",
                                         command=self.run_tests,
                                         padx=5,
                                         state='disabled')

        self.run_test_status_indicator_label = tk.Label(master=self,
                                                        text='Test status:')

        self.run_test_status_label = tk.Label(master=self,
                                              textvariable=self.run_test_status)

        # Widget positioning
        self.run_test_button.pack(side=tk.LEFT,
                                  padx=5)
        self.run_test_status_indicator_label.pack(side=tk.LEFT,
                                                  padx=5)
        self.run_test_status_label.pack(side=tk.LEFT,
                                        padx=5)

    def run_tests(self):
        pattern_data = self.pattern_table.get_data()
        velocity_data = self.velocity_table.get_data()
        position_data = self.position_table.get_data()

        if velocity_data:
            if self.velocity_table.should_randomize_data():
                random.shuffle(velocity_data)

        if position_data:
            if self.position_table.should_randomize_data():
                random.shuffle(position_data)

        if pattern_data:
            if not velocity_data and not position_data:
                self.launch_simple_test(pattern_data)
            elif not position_data:
                self.launch_test_with_velocity_replacement(pattern_data, velocity_data)
            elif not velocity_data:
                self.launch_test_with_positions(pattern_data, position_data)
        else:
            self.run_test_status.set('Enter a testing pattern.')

    def launch_simple_test(self, pattern_data):
        if pattern_data:
            send_command_to_start_running_MCU()
            self.self_sustained_single_testing(pattern_data, lambda: self.launch_simple_test(pattern_data))
        else:
            send_command_to_stop_running_MCU()
            self.run_test_status.set('No test running.')

    def launch_test_with_velocity_replacement(self, pattern_data, velocity_data):
        if velocity_data:
            velocity = velocity_data.pop(0)
            new_pattern_data = copy.deepcopy(pattern_data)
            for row in new_pattern_data:
                if row[1] == "VELOCITY":
                    row[1] = velocity[0]
            send_command_to_start_running_MCU()
            self.self_sustained_single_testing(new_pattern_data,
                                               lambda: self.launch_test_with_velocity_replacement(pattern_data,
                                                                                                  velocity_data))
        else:
            send_command_to_stop_running_MCU()
            self.run_test_status.set('No test running.')

    def launch_test_with_positions(self, pattern_data, position_data):
        if position_data and not self.waiting_for_position:
            position = position_data.pop(0)[0]
            send_position_data_to_MCU(position)
            self.waiting_for_position = True
            self.run_test_status.set('Moving FB to position')
            self.after(int(get_time_to_move_to_position(position)),
                       lambda: self.launch_test_with_positions(pattern_data, position_data))
        elif self.waiting_for_position:
            self.waiting_for_position = False
            send_command_to_start_running_MCU()
            self.self_sustained_single_testing(copy.deepcopy(pattern_data),
                                               lambda: self.launch_test_with_positions(pattern_data, position_data))
        else:
            send_command_to_stop_running_MCU()
            self.run_test_status.set('No test running.')

    def self_sustained_single_testing(self, pattern_data, test_ending_callback):
        if pattern_data:
            row = pattern_data.pop(0)
            duration = row[0]
            velocity = row[1]
            torque_limit = row[2]
            send_velocity_to_MCU(velocity)
            send_torque_to_MCU(torque_limit)
            self.run_test_status.set(f'Test running:    Duration: {duration} s    Velocity: {velocity} rev/s    '
                                     f'Torque limit: {torque_limit} Nm')
            self.after(int(duration * 1000),
                       lambda: self.self_sustained_single_testing(pattern_data, test_ending_callback))
        else:
            # store results here?
            test_ending_callback()

    def enable_testing(self):
        self.run_test_button.config(state='normal')

    def disable_testing(self):
        self.run_test_button.config(state='disabled')


def send_velocity_to_MCU(velocity):
    print("Velocity sent to the MCU:")
    print(velocity)


def send_position_data_to_MCU(position):
    print("Position sent to the MCU:")
    print(position)


def send_torque_to_MCU(torque):
    print("Torque sent to the MCU:")
    print(torque)


def send_command_to_start_running_MCU():
    print("Start running MCU")


def send_command_to_stop_running_MCU():
    print("Stop running MCU")


def get_time_to_move_to_position(position):
    return position * 0.1 * 1000


class WindowGUI(tk.Tk):  # This is the base that will help use and add frames easily.

    def __init__(self, window_title, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tk.Tk.wm_title(self, window_title)

        self.control_board_port = CommWidget(parent=self,
                                             row=0,
                                             column=0,
                                             main_text='Control board COM port',
                                             connected_callback=self.control_board_connected_callback,
                                             disconnected_callback=self.control_board_disconnected_callback)

        self.torque_board_port = CommWidget(parent=self,
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
                                               column=0,
                                               pattern_table=self.pattern_table,
                                               velocity_table=self.velocity_table,
                                               position_table=self.position_table)

        self.run_test_widget = RunTestWidget(parent=self,
                                             row=4,
                                             column=0,
                                             pattern_table=self.pattern_table,
                                             velocity_table=self.velocity_table,
                                             position_table=self.position_table)

    def control_board_connected_callback(self):
        self.run_test_widget.enable_testing()

    def control_board_disconnected_callback(self):
        self.run_test_widget.disable_testing()


if __name__ == "__main__":
    mainWindow = WindowGUI(window_title='Clutch control')
    mainWindow.state('zoomed')
    mainWindow.mainloop()
