from enum import Enum
from CommWidget import PortContainer
import struct


class CommCodes(Enum):
    TURN_ON_LED = 1
    TURN_OFF_LED = 2
    ECHO_INTEGER = 3
    PREPARE_PWM_DUTY_CYCLE = 4
    UPDATE_PWM_DUTY_CYCLE = 5
    REQUEST_VELOCITY_MOTOR_PID_PARAMETERS = 6
    SET_VELOCITY_MOTOR_PID_KP = 7
    SET_VELOCITY_MOTOR_PID_KI = 8
    SET_VELOCITY_MOTOR_PID_KD = 9
    SET_VELOCITY_MOTOR_PID_KA = 10
    SET_VELOCITY_MOTOR_PID_SETPOINT = 11
    VELOCITY_MOTOR_PID_SWITCH = 12
    ADD_MEASUREMENT_NOISE_TO_SIMULATION = 13
    ADD_PERIODIC_TORQUE_DISTURBANCE_TO_SIMULATION = 14
    SET_FIELD_BLOCKER_STEPS_TO_MOVE = 15
    GET_FIELD_BLOCKER_POSITION = 16


class Packet(bytearray):
    def __init__(self, code: CommCodes, value=None):
        super().__init__(10)

        self[0] = 0xA0 + (code.value & 0x1F)

        if type(value) is int:
            value_bytes = struct.pack('i', value)
        elif type(value) is float:
            value_bytes = struct.pack('f', value)
        else:
            value_bytes = struct.pack('i', 0)

        for i in range(0, 4):
            self[2 * i + 2] = value_bytes[i] & 0x0F
            self[2 * i + 3] = (value_bytes[i] & 0xF0) >> 4


class TestDevice:
    def __init__(self, control_port: PortContainer, torque_port: PortContainer,
                 control_time_base: float, torque_time_base: float,
                 field_blocker_velocity=1, gear_ratio=1):
        self.field_blocker_velocity = field_blocker_velocity
        self.gear_ratio = gear_ratio
        self.codes = CommCodes
        self.control_port = control_port
        self.torque_port = torque_port
        self.control_time_base = control_time_base
        self.torque_time_base = torque_time_base

        self.start_packet = Packet(self.codes.VELOCITY_MOTOR_PID_SWITCH, 1)
        self.stop_packet = Packet(self.codes.VELOCITY_MOTOR_PID_SWITCH, 2)
        self.get_position_packet = Packet(self.codes.GET_FIELD_BLOCKER_POSITION, 0)

    def start(self):
        self.control_port.write(self.start_packet)

    def stop(self):
        self.control_port.write(self.stop_packet)

    def send_position(self, position):
        current_position = self.get_position()
        steps_to_take = int(position - current_position)
        self.control_port.write(Packet(self.codes.SET_FIELD_BLOCKER_STEPS_TO_MOVE, steps_to_take))

    def send_velocity(self, velocity):
        self.control_port.write(Packet(self.codes.SET_VELOCITY_MOTOR_PID_SETPOINT, velocity * self.gear_ratio))

    def get_position(self):
        self.control_port.write(self.get_position_packet)
        return self.control_port.read_int32()

    def send_torque_limit(self, torque_limit):
        print("Torque sent to the MCU:")
        print(torque_limit)

    def get_time_to_move_to_position(self, position):
        current_position = self.get_position()
        steps_to_take = position - current_position
        print(f'Current position: {current_position}  Steps to take: {steps_to_take} Time to move:' +
              str(abs(steps_to_take * self.field_blocker_velocity) + 1))
        return abs(steps_to_take * self.field_blocker_velocity) + 1

    def flush_data(self):
        self.control_port.flush()

    def get_control_data(self):  # Modify according to the data I should be receiving
        return (self.control_port.read_float(),
                self.control_port.read_float())

    def get_torque_data(self):  # Modify according to the data I should be receiving
        return self.torque_port.read_float()
