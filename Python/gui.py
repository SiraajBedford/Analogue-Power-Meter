#import matplotlib
#matplotlib.use("TkAgg")
#from matplotlib import style
#
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#from matplotlib.figure import Figure 

from tkinter import Tk, ttk, mainloop, Frame, Text, END
from connection import ConnectionStatus, BeetleConnection


from time import sleep

class ConnectionFrame(Frame):
    def __create_connection(self):
        self.connection = BeetleConnection()

        def connection_callback(state):
            if state == ConnectionStatus.DISCONNECTED:
                self.event_disconnected()
            elif state == ConnectionStatus.CONNECTED:
                self.event_connected()
            elif state == ConnectionStatus.FAILED_TO_CONNECT:
                self.event_failed_to_connect()
            elif state == ConnectionStatus.DISCONNECTED_TIMEOUT:
                self.event_disconnected_timeout()
            elif state == ConnectionStatus.DISCONNECTED_ERROR:
                self.event_disconnected_error()
            else:
                raise Exception("Unhandled connection callback")

        self.connection.register_status_callback(connection_callback)

    def __set_connected_button(self):
        def connect_button_callback():
            self.connection.disconnect()

        self.connection.write(b"U")
        self.connection.write(b"\n")

        self.connect_button["command"] = connect_button_callback
        self.connect_button["text"] = "Disconnect"
        self.device_picker["state"] = "disabled"

    def __set_disconnected_button(self):
        def connect_button_callback():
            device = self.device_picker.get()
            self.connection.connect(device)

        self.connect_button["command"] = connect_button_callback
        self.connect_button["text"] = "Connect"

        self.device_picker["state"] = "normal"

    def __init__(self, main):
        self.main = main
        Frame.__init__(self, self.main.window, relief="ridge")

        self.__create_connection()

        self.device_label = ttk.Label(self, text="Device")
        self.device_label.grid(column=0, row=0, sticky="W")

        self.connection_label = ttk.Label(self, text="Connection")
        self.connection_label.grid(column=0, row=1, sticky="W")

        self.device_picker = ttk.Combobox(self, values=())
        self.device_picker.grid(column=1, row=0, sticky="WE", columnspan=2)

        self.connection_status_label = ttk.Label(self, text="")
        self.connection_status_label.grid(column=1, row=1, sticky="WE", columnspan=2)

        self.connect_button = ttk.Button(self, text="Connect")
        self.connect_button.grid(column=0, row=2, sticky="WE", columnspan=2)

        self.clear_button = ttk.Button(self, text="Clear all")
        self.clear_button.grid(column=2, row=2, sticky="WE")

        self.type_label = ttk.Label(self, text="Type : ")
        self.type_label.grid(column=0, row=4, sticky="W")

        self.type_entry = ttk.Entry(self)
        self.type_entry.grid(column=0, row=4, sticky="E")

        self.port_label = ttk.Label(self, text="Port : ")
        self.port_label.grid(column=1, row=4, sticky="W")

        self.port_entry = ttk.Entry(self)
        self.port_entry.grid(column=1, row=4, sticky="E")

        self.Uptime_button = ttk.Button(self, command = self.UptimeReturn, text="Uptime")
        self.Uptime_button.grid(column=2, row=4, sticky="WE")

        self.request_button = ttk.Button(self,command = self.SendRequest, text="Send Request")
        self.request_button.grid(column=0, row=5, sticky="WE", columnspan=1)
        

        self.return_text = Text(self)
        self.return_text.config(state='disabled')
        self.return_text.grid(column=0, row=6, sticky="WE", columnspan=3)
        self.return_text.see("end")
        self.clear()
        
    
        
        self.Uptime_button = ttk.Button(self, command = self.ResetTrip, text="Reset Trip")
        self.Uptime_button.grid(column=0, row=7, sticky="WE",columnspan=3)
        
        
        self.request_button = ttk.Button(self,command = self.DebugModeON, text="Debug Mode ON")
        self.request_button.grid(column=1, row=5, sticky="WE", columnspan=1)
        
        self.request_button = ttk.Button(self,command = self.DebugModeOFF, text="Debug Mode OFF")
        self.request_button.grid(column=2, row=5, sticky="WE", columnspan=1)
        
#        self.Uptime_button = ttk.Button(self, command = self.NB, text="New Button")
#        self.Uptime_button.grid(column=4, row=7, sticky="WE",columnspan=1)
        
        
        

        self.DEBUGMODE = False
        self.main.window.after(2000, self.refresh_debug)#self.printSerialReturn())

        def clear_button_callback():
            self.clear()

        self.clear_button["command"] = clear_button_callback

    def refresh_debug(self):

        if self.DEBUGMODE == True and self.connection.is_connected():
            self.printSerialReturn()
        self.main.window.after(2000, self.refresh_debug)#self.printSerialReturn())

    def event_connected(self):
        self.connection_label["text"] = "Connected"

        self.__set_connected_button()

    def event_disconnected(self):
        self.connection_label["text"] = "Disconnected"

        self.__set_disconnected_button()

    def event_disconnected_timeout(self):
        self.connection_label["text"] = "Disconnected (Timeout)"

        self.__set_disconnected_button()

    def event_disconnected_error(self):
        self.connection_label["text"] = "Disconnected (Error)"

        self.__set_disconnected_button()

    def event_failed_to_connect(self):
        self.connection_label["text"] = "Disconnected (Failed to connect)"

        self.__set_disconnected_button()

    def SendRequest(self):
        CommandType = self.type_entry.get()  #String is saved in Command
        CommandPort = self.port_entry.get()

        if not self.connection.is_connected():
            self.connection_status_label["text"] = "Cannot write when not connected"
            return

        # Entry validation:
        if CommandType not in ['0','1','2','X','x']:
            txt = "Please enter valid type (0,1,2,X)"
            self.connection_status_label["text"] = txt
            return

        else:
            self.connection_status_label["text"] = ''

        if CommandType == '1':
            if CommandPort not in ['0','1','2']:
                txt = "Please enter valid analogue port number (0,1,2)"
                self.connection_status_label["text"] = txt
                return

        elif CommandType == '2':
            if CommandPort not in ['0','1','2']:
                txt = "Please enter valid digital port number (0,1,2)"
                self.connection_status_label["text"] = txt
                return


        elif CommandType in ['x','X']:
            if CommandPort not in ['0','1']:
                txt = "Please enter 0 (debug off) or 1 (debug on) in port field"
                self.connection_status_label["text"] = txt
                return
            else:
                if CommandPort == '1':
                    self.DEBUGMODE = True
                    self.return_text.config(state='normal')
                    self.return_text.insert(END,"\n"+'Debug-Mode On')
                    self.return_text.config(state='disabled')
                    self.return_text.see("end")

                    self.connection.write(CommandType.encode('utf-8'))
                    self.connection.write(CommandPort.encode('utf-8'))
                else:
                    self.DEBUGMODE = False
                    self.type_entry.config(state='normal')

                    self.return_text.config(state='normal')
                    self.return_text.insert(END,"\n"+'Debug-Mode Off')
                    self.return_text.config(state='disabled')
                    self.return_text.see("end")

                    self.connection.write(CommandType.encode('utf-8'))
                    self.connection.write(CommandPort.encode('utf-8'))
        else:
            self.connection_status_label["text"] = ''

        self.connection.write(CommandType.encode('utf-8'))
        self.connection.write(CommandPort.encode('utf-8'))
        self.connection.write(b"\n")
        self.printSerialReturn()

    def printSerialReturn(self):
        sleep(0.02)
        OutputText = self.CleanList(self.connection.receive())

        if OutputText != '[]':
            self.return_text.config(state='normal')
            self.return_text.insert(END,"\n"+OutputText)
            self.return_text.config(state='disabled')
            self.return_text.see("end")

    def CleanList(self,InputList):
        OutputString = "["
        for returnstring in range(0,len(InputList)):
            if (returnstring != (len(InputList) - 1)):
                OutputString += str(InputList[returnstring][:-1]) + ', '
            else:
                OutputString += str(InputList[returnstring][:-1])

        OutputString += "]"
        return OutputString

    def UptimeReturn(self):
        if self.connection.is_connected():
            self.connection.write(b"U")
            self.connection.write(b"\n")
            self.printSerialReturn()
            
            
    def DebugModeON(self):
        
                if self.connection.is_connected():
                    self.connection.write(b"X1")
                    self.connection.write(b"\n")
                    self.printSerialReturn()
                    self.DEBUGMODE = True
                    self.return_text.config(state='normal')
                    self.return_text.insert(END,"\n"+'Debug-Mode On')
                    self.return_text.config(state='disabled')
                    self.return_text.see("end")
                    
    def DebugModeOFF(self):
        
                if self.connection.is_connected():
                    self.connection.write(b"X0")
                    self.connection.write(b"\n")
                    self.DEBUGMODE = False
                    self.type_entry.config(state='normal')
                    self.return_text.config(state='normal')
                    self.return_text.insert(END,"\n"+'Debug-Mode Off')
                    self.return_text.config(state='disabled')
                    self.return_text.see("end")
                    self.printSerialReturn()
            
            
    def ResetTrip(self):
        if  self.connection.is_connected():
            self.return_text.config(state='normal');
            self.return_text.insert(END,"\n"+'Latch Reset was sent');
            self.return_text.config(state='disabled');
            self.return_text.see("end");
            self.connection.write(b"R")
            self.connection.write(b"\n")
            self.printSerialReturn()
            

    def clear(self):

        if self.connection.is_connected():

            self.return_text.config(state='normal')
            self.return_text.delete(1.0,END)
            self.return_text.config(state='disabled')
            self.type_entry.delete(0,'end')
            self.port_entry.delete(0,'end')
            self.type_entry.config(state='normal')
            self.port_entry.config(state='normal')
            self.request_button.config(state='normal')
        else:
            self.return_text.config(state='normal')
            self.return_text.delete(1.0,END)
            self.return_text.config(state='disabled')
            self.type_entry.delete(0,'end')
            self.port_entry.delete(0,'end')
            self.type_entry.config(state='normal')
            self.port_entry.config(state='normal')
            self.request_button.config(state='normal')

            self.device_list = BeetleConnection.possible_connections()

            possible_values = [
                x.device for x in self.device_list if "Arduino" in str(x)
            ]
            self.device_picker["values"] = possible_values
            if len(possible_values) > 0:
                self.device_picker.current(0)
            self.event_disconnected()

class Main:

    def __init__(self):
        self.window = Tk()

        self.connection_frame = ConnectionFrame(self)
        self.connection_frame.grid(row=0, sticky="NWE", columnspan=3)

        self.window.resizable(True, True)
        self.window.mainloop()


#class Two(tk.frame):
#    
#    def __init__(self, parent, controller):
#        tk.Frame.__init__(self, parent)
#        label=tk.Label.self



Main()

