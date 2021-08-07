import time
import tkinter as tk
import random
import copy
from TableWidgets import PatternTableWidget
from TableWidgets import ParameterTableWidget
from TestDevice import TestDevice


class RunTestWidget(tk.Frame):
    def __init__(self, parent, row, column, device: TestDevice, pattern_table: PatternTableWidget,
                 velocity_table: ParameterTableWidget, position_table: ParameterTableWidget):
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
        self.device = device

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
                if row[1] == "VELOCITY":
                    row[1] = velocity[0]
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
            row = pattern_data.pop(0)
            duration = row[0]
            velocity = row[1]
            torque_limit = row[2]
            self.device.send_velocity(velocity)
            self.device.send_torque_limit(torque_limit)
            self.run_test_status.set(f'Test running:    Duration: {duration} s    Velocity: {velocity} rev/s    '
                                     f'Torque limit: {torque_limit} Nm')
            self.after(int(duration * 1000),
                       lambda: self.self_sustained_single_testing(pattern_data, test_ending_callback))
        else:
            self.device.stop()
            time.sleep(1)
            self.run_test_status.set('Processing and storing data')  # Doesn't have to happen here.
            self.device.flush_data()
            self.after(2000, test_ending_callback)

    def enable_testing(self):
        self.run_test_button.config(state='normal')

    def disable_testing(self):
        self.run_test_button.config(state='disabled')