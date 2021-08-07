import tkinter as tk
import random
import copy
from TableWidgets import PatternTableWidget
from TableWidgets import ParameterTableWidget
from TestDevice import TestDevice
from numpy import linspace
import numpy as np
import os
import csv
import datetime
import math

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class RunTestWidget(tk.Frame):
    def __init__(self, parent, row, column, device: TestDevice, pattern_table: PatternTableWidget,
                 velocity_table: ParameterTableWidget, position_table: ParameterTableWidget,
                 store_folder: tk.StringVar, time_between_tests=1):
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

        self.position_at_test_start = None
        self.waiting_for_position = False

        self.device = device
        self.time_between_tests = time_between_tests

        self.control_test_data = []
        self.torque_test_data = []
        self.pattern_table_to_store = []
        self.store_folder = store_folder

        # Frames for plots
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill=tk.BOTH, expand=1)
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

        # Plot member variables
        self.control_result_figure = Figure(figsize=(2, 2), dpi=100)
        self.control_result_axis = self.control_result_figure.add_subplot()
        self.control_result_lines = [self.control_result_axis.plot([], [])[0],
                                     self.control_result_axis.plot([], [])[0]]
        self.control_result_canvas = FigureCanvasTkAgg(self.control_result_figure,
                                                       master=self.bottom_frame)  # A tk.DrawingArea.
        self.control_result_canvas.draw()

        self.torque_result_figure = Figure(figsize=(2, 2), dpi=100)
        self.torque_result_axis = self.torque_result_figure.add_subplot()
        self.torque_result_line = self.torque_result_axis.plot([], [])[0]
        self.torque_result_canvas = FigureCanvasTkAgg(self.torque_result_figure,
                                                      master=self.bottom_frame)  # A tk.DrawingArea.
        self.torque_result_canvas.draw()

        # Widget member variables
        self.run_test_button = tk.Button(master=self.top_frame,
                                         height=1,
                                         text="Run test",
                                         command=self.run_tests,
                                         padx=5,
                                         state='disabled')

        self.run_test_status_indicator_label = tk.Label(master=self.top_frame,
                                                        text='Test status:')

        self.run_test_status_label = tk.Label(master=self.top_frame,
                                              textvariable=self.run_test_status)

        # Widget positioning
        self.run_test_button.pack(side=tk.LEFT,
                                  padx=5)
        self.run_test_status_indicator_label.pack(side=tk.LEFT,
                                                  padx=5)
        self.run_test_status_label.pack(side=tk.LEFT,
                                        padx=5)

        self.control_result_canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=5)
        self.torque_result_canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=1, pady=5)

    def run_tests(self):
        pattern_data = self.pattern_table.get_data()
        velocity_data = self.velocity_table.get_data()
        position_data = self.position_table.get_data()

        if pattern_data:
            self.disable_testing()
            if not velocity_data and not position_data:
                self.launch_simple_test(pattern_data)
            elif not position_data:
                if self.velocity_table.should_randomize_data():
                    random.shuffle(velocity_data)
                self.launch_test_with_velocity_replacement(pattern_data, velocity_data)
            else:
                if self.position_table.should_randomize_data():
                    random.shuffle(position_data)
                self.launch_test_with_positions(pattern_data, position_data, velocity_data)
        else:
            self.run_test_status.set('Enter a testing pattern.')

    def launch_simple_test(self, pattern_data, ending_call_back=None):
        if pattern_data:
            self.position_at_test_start = self.device.get_position()
            self.pattern_table_to_store = copy.deepcopy(pattern_data)
            self.device.start()
            self.self_sustained_single_testing(pattern_data, lambda: self.launch_simple_test(pattern_data,
                                                                                             ending_call_back))
        else:
            self.run_test_status.set('No tests running.')
            if ending_call_back:
                ending_call_back()
            else:
                self.enable_testing()

    def launch_test_with_velocity_replacement(self, pattern_data, velocity_data, ending_call_back=None):
        if velocity_data:
            velocity = velocity_data.pop(0)
            new_pattern_data = copy.deepcopy(pattern_data)
            for row in new_pattern_data:
                if row[1] == 'VELOCITY':
                    row[1] = velocity[0]
                if row[0] == 'TIME':
                    row[0] = math.ceil(1 / row[1])  # TODO: Double check that this is the correct formula
            self.launch_simple_test(new_pattern_data,
                                    lambda: self.launch_test_with_velocity_replacement(pattern_data,
                                                                                       velocity_data,
                                                                                       ending_call_back))
        else:
            if ending_call_back:
                ending_call_back()
            else:
                self.enable_testing()

    def launch_test_with_positions(self, pattern_data, position_data, velocity_data=None):

        if position_data and not self.waiting_for_position:
            position = position_data.pop(0)[0]
            self.device.send_position(position)
            self.waiting_for_position = True
            self.run_test_status.set('Moving FB to position')
            self.after(int(self.device.get_time_to_move_to_position(position) * 1000),
                       lambda: self.launch_test_with_positions(pattern_data,
                                                               position_data,
                                                               velocity_data))
        elif self.waiting_for_position:
            self.waiting_for_position = False
            if not velocity_data:
                self.launch_simple_test(copy.deepcopy(pattern_data),
                                        lambda: self.launch_test_with_positions(pattern_data,
                                                                                position_data,
                                                                                velocity_data))
            else:
                if self.velocity_table.should_randomize_data():
                    random.shuffle(velocity_data)
                self.launch_test_with_velocity_replacement(pattern_data,
                                                           copy.deepcopy(velocity_data),
                                                           lambda: self.launch_test_with_positions(pattern_data,
                                                                                                   position_data,
                                                                                                   velocity_data))
        else:
            self.enable_testing()

    def self_sustained_single_testing(self, pattern_data, test_ending_callback):
        if pattern_data:
            duration, velocity, torque_limit = pattern_data.pop(0)

            self.device.send_velocity(velocity)
            self.device.send_torque_limit(torque_limit)
            self.run_test_status.set(f'Test running:    Duration: {duration} s    Velocity: {velocity} rev/s    '
                                     f'Torque limit: {torque_limit} Nm')
            self.after(int(duration * 1000),
                       lambda: self.self_sustained_single_testing(pattern_data, test_ending_callback))
        else:
            self.device.stop()
            self.after(1000, lambda: self.store_data(test_ending_callback))

    def enable_testing(self):
        self.run_test_button.config(state='normal')

    def disable_testing(self):
        self.run_test_button.config(state='disabled')

    def store_data(self, test_ending_call_back):
        self.run_test_status.set('Processing and storing data.')

        max_time = sum([row[0] for row in self.pattern_table_to_store])

        # Just for testing
        test_control_time = linspace(0, max_time, int(max_time / self.device.control_time_base) + 1)  # Also fake

        frequency_1 = random.random() * 10
        frequency_2 = random.random() * 10
        for t in test_control_time:
            # self.control_test_data.append([t, *self.device.get_control_data()])
            self.control_test_data.append([t,
                                           10 * np.sin(np.pi * frequency_1 * t),
                                           5 * np.sin(np.pi * frequency_2 * t)])

        self.redraw_control_results_plot()

        test_torque_time = linspace(0, max_time, int(max_time / self.device.torque_time_base) + 1)  # Also fake
        frequency_3 = random.random() * 10

        for t in test_torque_time:
            # self.torque_test_data.append([t, *self.device.get_torque_data()])
            self.torque_test_data.append([t, 2.5 * np.sin(np.pi * frequency_3 * t)])

        self.redraw_torque_results_plot()

        control_data_path, pattern_data_path, torque_data_path = self.create_and_get_test_data_folders()
        file_name = self.get_file_name_for_test_results()
        with open(control_data_path + file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.control_test_data)
        with open(pattern_data_path + file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.pattern_table_to_store)
        with open(torque_data_path + file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.torque_test_data)
        self.clean_up_test_data()

        self.run_test_status.set(f'Obligatory time between tests: {self.time_between_tests} s.')
        self.after(1000 * self.time_between_tests, test_ending_call_back)

    def clean_up_test_data(self):
        self.pattern_table_to_store = []
        self.control_test_data = []
        self.torque_test_data = []

    def get_file_name_for_test_results(self):
        file_name = '/' + str(self.position_at_test_start) + '_' + str(datetime.datetime.now()) + '.csv'
        file_name = file_name.replace(' ', '_')
        file_name = file_name.replace(':', '_')
        return file_name

    def create_and_get_test_data_folders(self):
        control_data_path = self.store_folder.get() + '/CONTROL_DATA'
        torque_data_path = self.store_folder.get() + '/TORQUE_DATA'
        pattern_data_path = self.store_folder.get() + '/PATTERN_DATA'
        if not os.path.exists(control_data_path):
            os.makedirs(control_data_path)
        if not os.path.exists(torque_data_path):
            os.makedirs(torque_data_path)
        if not os.path.exists(pattern_data_path):
            os.makedirs(pattern_data_path)
        return control_data_path, pattern_data_path, torque_data_path

    def redraw_control_results_plot(self):
        new_x = [row[0] for row in self.control_test_data]
        new_y = [[row[1] for row in self.control_test_data],
                 [row[2] for row in self.control_test_data]]

        for index, line in enumerate(self.control_result_lines):
            line.set_xdata(new_x)
            line.set_ydata(new_y[index])

        self.control_result_axis.set_xlim(new_x[0], new_x[-1])
        self.control_result_axis.set_ylim(np.min(new_y) * 1.1, np.max(new_y) * 1.1)
        self.control_result_canvas.draw()

    def redraw_torque_results_plot(self):
        new_x = [row[0] for row in self.torque_test_data]
        new_y = [row[1] for row in self.torque_test_data]

        self.torque_result_line.set_xdata(new_x)
        self.torque_result_line.set_ydata(new_y)

        self.torque_result_axis.set_xlim(new_x[0], new_x[-1])
        self.torque_result_axis.set_ylim(min(new_y) * 1.1, max(new_y) * 1.1)
        self.torque_result_canvas.draw()
