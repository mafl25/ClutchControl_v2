import tkinter as tk
from CommWidget import CommWidget
from TableWidgets import PatternTableWidget
from TableWidgets import ParameterTableWidget
from SaveAndLoadWidget import SaveAndLoadWidget
from RunTestWidget import RunTestWidget
from TestDevice import TestDevice


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

        self.device = TestDevice(field_blocker_velocity=0.005,
                                 gear_ratio=1 / 3,
                                 control_port=self.control_board_port.port)

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
                                             device=self.device,
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
