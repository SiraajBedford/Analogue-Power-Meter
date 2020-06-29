import serial
from serial.tools.list_ports import comports
from enum import Enum
from time import sleep

# Connection status enum that is sent to the callback
class ConnectionStatus(Enum):
    DISCONNECTED = 0
    CONNECTED = 1
    FAILED_TO_CONNECT = 2
    DISCONNECTED_TIMEOUT = 3#4
    DISCONNECTED_ERROR = 4


# BeetleConnection class
class BeetleConnection:
    connection_ = None
    callback = None
    last_error = None

    def __handle_callback(self, code):
        if self.callback is not None:
            self.callback(code)

    def __init__(self):
        self.isOpen = False
        self.buf = ''
        pass

    # Connect to a valid device
    #  If a callback is registered it will called with
    #  CONNECTED or FAILED_TO_CONNECT
    def connect(self, device):
        self.isOpen = True
        if device == "":
            self.__handle_callback(ConnectionStatus.FAILED_TO_CONNECT)
            return

        try:
            self.connection_ = serial.Serial(device, 19200)
            self.connection_.write(bytearray([0, 0, 0]))
        except serial.SerialException as se:
            self.last_error = "{}".format(se)
            self.__handle_callback(ConnectionStatus.FAILED_TO_CONNECT)
            return

        self.__handle_callback(ConnectionStatus.CONNECTED)

    # Disconnect from device
    #  Only calls the callback with DISCONNECTED
    #
    def disconnect(self):
        self.isOpen = False
        if self.connection_ is not None:
            self.connection_.close()
            self.connection_ = None
        self.__handle_callback(ConnectionStatus.DISCONNECTED)

    # Returns wether or not the device is connected
    def is_connected(self):
        self.isOpen = True
        return self.connection_ is not None

    # Write data to the device
    #  If it's not connected an exception is thrown
    #  If something goes wrong during writing the callback is called
    #  with DISCONNECTED_TIMEOUT or DISCONNECTED_ERROR
    def write(self, data):
        if self.connection_ is None:
            raise Exception("LeonardoConnection: Cannot write when not connected")

        try:
            self.connection_.write(data)
        except serial.SerialTimeoutException:
            self.disconnect()
            self.last_error = "Timeout while writing"
            self.__handle_callback(ConnectionStatus.DISCONNECTED_TIMEOUT)
        except serial.SerialException as se:
            self.disconnect()
            self.last_error = "{}".format(se)
            self.__handle_callback(ConnectionStatus.DISCONNECTED_ERROR)

    ## Method for receiving serial data from the Arduino
    ## Empties the serial buffer into self.buf
    ## Separates messages on newline characters ('\n') and stores all the received messages in an array
    def receive(self):
        messageArray = []
        numCharsRead = 0
        numNewLines = 0
        if (self.isOpen):
            if self.connection_ != None:
                while(self.connection_.inWaiting() > 0):
                    readCharacter = self.connection_.read().decode("ascii")
                    self.buf = self.buf + readCharacter
                    numCharsRead += 1
                if (numCharsRead > 0 and ('\n' in self.buf)):
                    leftover = self.buf.rsplit('\n',1)
                    messageArray = leftover[0].split('\n')
                    self.buf = leftover[1]
        else:
            raise Exception("BeetleConnection: Cannot read when not connected")
        return messageArray

    # Register the callback function to be used
    #  Overwrites the previous callback
    def register_status_callback(self, callback):
        self.callback = callback

    # Remove the callback
    def clear_status_callback(self):
        self.register_status_callback(None)

    # Return a list of possible connections
    @staticmethod
    def possible_connections():
        return comports()
