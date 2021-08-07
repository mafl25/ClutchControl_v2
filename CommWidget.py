import tkinter as tk
import serial.tools.list_ports as ports
from serial import Serial
from serial import SerialException
import struct


def declare_globals():
    global FAKE_PORT_NAME
    FAKE_PORT_NAME = 'COM1 - Fake port for testing only'
    global USING_FAKE_PORT
    USING_FAKE_PORT = False


class PortContainer:
    def __init__(self, port=None):
        self.port = port

    def set(self, port):
        self.port = port

    def get(self):
        return self.port

    def write(self, *args, **kwargs):
        if self.port:
            self.port.write(*args, **kwargs)
        else:
            if USING_FAKE_PORT:
                print(args)

    def read(self, *args, **kwargs):
        if self.port:
            return self.port.read(*args, **kwargs)
        else:
            return None

    def open(self, *args, **kwargs):
        if self.port:
            self.port.open(*args, **kwargs)

    def close(self, *args, **kwargs):
        if self.port:
            self.port.close(*args, **kwargs)

    def flush(self, *args, **kwargs):
        if self.port:
            self.port.reset_input_buffer(*args, **kwargs)

    def read_int32(self):
        if self.port:
            data = self.read(size=4)
            return struct.unpack('i', data)[0]
        else:
            if USING_FAKE_PORT:
                return 100
            else:
                return None

    def read_float(self):
        if self.port:
            data = self.read(size=4)
            return struct.unpack('f', data)[0]
        else:
            if USING_FAKE_PORT:
                return 3.14
            else:
                return None


class CommWidget(tk.Frame):

    def __init__(self,
                 parent,
                 row,
                 column,
                 main_text,
                 connected_callback=None,
                 disconnected_callback=None,
                 baud_rate=921600):
        super().__init__(parent)

        declare_globals()

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

        self.baud_rate = baud_rate
        self.port = PortContainer()

        # Widget member variables
        port_list = ports.comports()
        if not port_list:
            port_list = [FAKE_PORT_NAME]
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
        if not port_list:
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
                port_name = self.menu_main_text.get().partition(' ')[0]
                try:
                    if self.menu_main_text.get() != FAKE_PORT_NAME:
                        self.port.set(Serial(port=port_name, baudrate=self.baud_rate, timeout=0.1))
                    else:
                        global USING_FAKE_PORT
                        USING_FAKE_PORT = True
                    self.is_connected = True
                    self.status_text.set('Connected')
                    if self.connected_callback:
                        self.connected_callback()
                except SerialException:
                    self.port.set(None)
                    self.status_text.set('Connection failed')
            else:
                self.status_text.set('Port not selected')
        elif self.is_connected is True:
            self.is_connected = False
            self.status_text.set('Not connected')
            self.port.close()
            self.port.set(None)
            if self.disconnected_callback:
                self.disconnected_callback()
