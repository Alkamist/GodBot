import configparser
import enum
import os
import hashlib
import zmq

def hash_string(s):
  return hashlib.md5(s.encode()).hexdigest()

def hash_port_path(s):
  return 5536 + int(hash_string(s), 16) % 60000

@enum.unique
class Button(enum.Enum):
    A = 0
    B = 1
    X = 2
    Y = 3
    Z = 4
    START = 5
    L = 6
    R = 7
    D_UP = 8
    D_DOWN = 9
    D_LEFT = 10
    D_RIGHT = 11

@enum.unique
class Trigger(enum.Enum):
    L = 0
    R = 1

@enum.unique
class Stick(enum.Enum):
    MAIN = 0
    C = 1

class Gamepad:
    def __init__(self, port_number, dolphin):
        self.port_number = port_number
        self.dolphin = dolphin
        self.create_configuration()

        self.pipes_directory = self.dolphin.user_directory + "/Pipes"
        if not os.path.exists(self.pipes_directory):
            os.makedirs(self.pipes_directory)

        context = zmq.Context()
        self.port_path = self.pipes_directory + "/Bot2"
        self.port_hash = hash_port_path(self.port_path)

        with open(self.port_path, 'w') as f:
            f.write(str(self.port_hash))

        self.socket = context.socket(zmq.PUSH)
        address = "tcp://127.0.0.1:%d" % self.port_hash
        self.socket.bind(address)

        self.message = ""

    def create_configuration(self):
        #Read in dolphin's controller config file
        config = configparser.SafeConfigParser()
        controller_config_file = self.dolphin.user_directory + "/Config/GCPadNew.ini"
        config.read(controller_config_file)

        #Add a bot standard controller config to the given port
        section = "GCPad" + str(self.port_number)
        if not config.has_section(section):
            config.add_section(section)

        config.set(section, 'Device', 'Pipe/0/Bot' + str(self.port_number))
        config.set(section, 'Buttons/A', 'Button A')
        config.set(section, 'Buttons/B', 'Button B')
        config.set(section, 'Buttons/X', 'Button X')
        config.set(section, 'Buttons/Y', 'Button Y')
        config.set(section, 'Buttons/Z', 'Button Z')
        config.set(section, 'Buttons/L', 'Button L')
        config.set(section, 'Buttons/R', 'Button R')
        config.set(section, 'Main Stick/Up', 'Axis MAIN Y +')
        config.set(section, 'Main Stick/Down', 'Axis MAIN Y -')
        config.set(section, 'Main Stick/Left', 'Axis MAIN X -')
        config.set(section, 'Main Stick/Right', 'Axis MAIN X +')
        config.set(section, 'Triggers/L', 'Button L')
        config.set(section, 'Triggers/R', 'Button R')
        config.set(section, 'Main Stick/Modifier', 'Shift_L')
        config.set(section, 'Main Stick/Modifier/Range', '50.000000000000000')
        config.set(section, 'D-Pad/Up', 'T')
        config.set(section, 'D-Pad/Down', 'G')
        config.set(section, 'D-Pad/Left', 'F')
        config.set(section, 'D-Pad/Right', 'H')
        config.set(section, 'Buttons/Start', 'Button START')
        config.set(section, 'Buttons/A', 'Button A')
        config.set(section, 'C-Stick/Up', 'Axis C Y +')
        config.set(section, 'C-Stick/Down', 'Axis C Y -')
        config.set(section, 'C-Stick/Left', 'Axis C X -')
        config.set(section, 'C-Stick/Right', 'Axis C X +')
        config.set(section, 'Triggers/L-Analog', 'Axis L -+')
        config.set(section, 'Triggers/R-Analog', 'Axis R -+')

        with open(controller_config_file, 'w') as configfile:
            config.write(configfile)

        #Indexed at 0. "6" means standard controller, "12" means GCN Adapter
        self.dolphin.change_settings([
            ["Core", 'SIDevice' + str(self.port_number - 1), "6"]
        ])

    def write(self, command, buffering=False):
        self.message += command + '\n'
        if not buffering:
            self.flush()

    def flush(self):
        self.socket.send_string(self.message)
        self.message = ""

    def press_button(self, button, buffering=False):
        """Press a button."""
        assert button in Button
        self.write('PRESS {}'.format(button.name), buffering)

    def release_button(self, button, buffering=False):
        """Release a button."""
        assert button in Button
        self.write('RELEASE {}'.format(button.name), buffering)

    def press_trigger(self, trigger, amount, buffering=False):
        """Press a trigger. Amount is in [0, 1], with 0 as released."""
        assert trigger in Trigger
        self.write('SET {} {:.2f}'.format(trigger.name, amount), buffering)

    def tilt_stick(self, stick, x, y, buffering=False):
        """Tilt a stick. x and y are in [0, 1], with 0.5 as neutral."""
        assert stick in Stick
        self.write('SET {} {:.2f} {:.2f}'.format(stick.name, x, y), buffering)

    def send_controller(self, controller):
        for button in Button:
            field = 'button_' + button.name
            if hasattr(controller, field):
                if getattr(controller, field):
                    self.press_button(button, True)
                else:
                    self.release_button(button, True)

        # for trigger in Trigger:
        #     field = 'trigger_' + trigger.name
        #     self.press_trigger(trigger, getattr(controller, field))

        for stick in Stick:
            field = 'stick_' + stick.name
            value = getattr(controller, field)
            self.tilt_stick(stick, value.x, value.y, True)

        self.flush()
