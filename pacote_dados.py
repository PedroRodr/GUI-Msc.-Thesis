import tkinter as tk
from tkinter import Canvas, Label, StringVar, Text, Variable, ttk, messagebox
from PIL import ImageTk, Image
import serial
import sys
import time
import glob
from serial.tools.list_ports import comports
from dataclasses import dataclass # Declaração da classe de comandos
import numpy as np
DATA_SIZE = 8
@dataclass
class CommandDef:
    function: int    # uint8_t
    value: int       # uint32_t  
    size: int        # uint8_t
    data: np.array # uint8_t[DATA_SIZE]
    crc: int         # uint8_t
    control: int     # uint8_t
    
    def __init__(self, function=0, value=0, size=0, data=None, crc=0, control=0x7e):
        self.function = function & 0xFF
        self.value = value & 0xFFFFFFFF
        self.size = size & 0xFF
        self.data = data if data is not None else np.zeros(DATA_SIZE, dtype=np.uint8)
        self.crc = crc & 0xFF
        self.control = control & 0xFF

    
    def to_bytes(self):
        """Convert command to bytes for UART transmission"""
        # Calculate CRC before sending        
        # Pack all fields into byte array
        byte_array = bytearray()
        byte_array.append(self.function)
        byte_array.extend(self.value.to_bytes(4, 'little'))
        byte_array.append(self.size)
        byte_array.extend(self.data[:self.size])  # Only send 'size' bytes of data
        byte_array.append(self.crc)
        byte_array.append(self.control)
        
        return bytes(byte_array)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('SEP GUI')

        # layout on the root window
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=2)

        # background of the root window
        self.config(bg='white')

        self.__create_widgets()

    def __create_widgets(self):

        logo_frame = LogoFrame(self)
        logo_frame.grid(column=1, row=0, sticky='we')
        # create the input frame
        BUTTON_frame = BUTTONframe(self, logo_frame)
        BUTTON_frame.grid(column=1, row=5, sticky='sw')

        for widget in self.winfo_children():
            widget.grid(padx=30, pady=10)


class LogoFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.config(bg='white')
        self.__create_widgets()

    def callback(self, event):
        print(self.menu.get())
        self.com = self.menu.get()
        self.port = serial.Serial(self.com, 115200, timeout=2)

    def __create_widgets(self):
        self.img = ImageTk.PhotoImage(Image.open(
            'GUI/ist.png').resize((100, 97), Image.LANCZOS))
        self.canvas = tk.Canvas(
            self, bg="white", width=250, height=97, bd=0, highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_image(75, 0, image=self.img, anchor='nw')

        self.aval_ports = serial_ports()
   
        self.com = 0

        self.menu = ttk.Combobox(
            self, values=self.aval_ports)
        self.menu.set('Please choose the COM port')
        self.menu.bind("<<ComboboxSelected>>", self.callback)
        self.menu.pack(side='bottom', fill='x', pady=(20,0))



class BUTTONframe(tk.Frame):
    def __init__(self, container, logo_frame):
        super().__init__(container)
        # setup the grid layout manager
        self.logo = logo_frame
        self.columnconfigure(1, weight=1)
        self.config(bg='white')
        self.__create_widgets()


    def button_command(self):
        if self.logo.com == 0:
            messagebox.showwarning('Warning', 'Please select COM port')
        else:
            self.button.config(image=self.off_switch)
            
            print('\n NOVO TESTE \n')

            print('Status: ----------------------')
            cmd = CommandDef(function=0x13, value=1000, size=32)
            cmd.data[0] = 0x11
            cmd.data[1] = 0x7E
            cmd.data[2] = 0x22
            cmd.data[3] = 0x33
            cmd.data[4] = 0x44
            cmd.data[5] = 0x55
            cmd.data[6] = 0x66
            cmd.data[7] = 0x77


            data_to_send = cmd.to_bytes()
            #self.logo.port.flushOutput()     #Limpa o conteudo no buffer de escrita
            self.logo.port.write(data_to_send)
            self.logo.port.flush()
            print("Valor envidado em string: " + str(cmd))
            print("Valor envidado em bits: " + cmd.to_bytes().hex())
            response = self.logo.port.read(16)  # Expect 10 bytes back
            print(f"Response: {response.hex()}")


    def __create_widgets(self):

        self.off_switch = ImageTk.PhotoImage(Image.open(
            'GUI/button.png').resize((51, 51), Image.LANCZOS))

        # Button frame, label and button init
        self.button_frame = tk.Frame(self)
        self.button_frame.config(background='white')
        self.button_frame.grid(column=1, row=6, sticky='we', padx=(90, 0))
        self.button_label = tk.Label(
        self.button_frame, text='PRESS ME!!!', background='white')
        self.button_label.pack(side='bottom', padx=(0, 5))
        self.button = tk.Button(self.button_frame, background='white', bd=0,
                              highlightthickness=0, command=self.button_command, image=self.off_switch)
        self.button.pack(side='bottom')

        self.text_m1 = tk.Frame(self)
        self.text_m1.config(background='white')
        self.text_m1.grid(column=0, row=2, sticky='we', padx=(45, 0))
        self.text_label = tk.Label(
        self.text_m1, text='Status', background='white')
        self.text_label.pack(side='bottom', padx=(0, 5))

        self.text_m2 = tk.Frame(self)
        self.text_m2.config(background='white')
        self.text_m2.grid(column=0, row=3, sticky='we', padx=(45, 0))
        self.text_label = tk.Label(
        self.text_m2, text='Temperatura min', background='white')
        self.text_label.pack(side='bottom', padx=(0, 5))

        self.text_m3 = tk.Frame(self)
        self.text_m3.config(background='white')
        self.text_m3.grid(column=0, row=4, sticky='we', padx=(45, 0))
        self.text_label = tk.Label(
        self.text_m3, text='Temperatura max', background='white')
        self.text_label.pack(side='bottom', padx=(0, 5))

        self.text_idle = tk.Frame(self)
        self.text_idle.config(background='white')
        self.text_idle.grid(column=0, row=5, sticky='we', padx=(45, 0))
        self.text_label = tk.Label(
        self.text_idle, text='Tempo de Idle', background='white')
        self.text_label.pack(side='bottom', padx=(0, 5))

        self.input_m1 = tk.Frame(self)
        self.input_m1.config(background='white')
        self.input_m1.grid(column=1, row=2, sticky='we', padx=(45, 0))
        self.m1 = tk.Entry(self.input_m1)
        self.m1.pack(padx=5,pady=5)

        
        self.input_m2 = tk.Frame(self)
        self.input_m2.config(background='white')
        self.input_m2.grid(column=1, row=3, sticky='we', padx=(45, 0))
        self.m2 = tk.Entry(self.input_m2)
        self.m2.pack(padx=5,pady=5)


        self.input_m3 = tk.Frame(self)
        self.input_m3.config(background='white')
        self.input_m3.grid(column=1, row=4, sticky='we', padx=(45, 0))
        self.m3 = tk.Entry(self.input_m3)
        self.m3.pack(padx=5,pady=5)

        self.input_idle = tk.Frame(self)
        self.input_idle.config(background='white')
        self.input_idle.grid(column=1, row=5, sticky='we', padx=(45, 0))
        self.idle = tk.Entry(self.input_idle)
        self.idle.pack(padx=5,pady=5)

        #Leitura da temperatura
        self.temp_text = tk.Frame(self)
        self.temp_text.config(background='white')
        self.temp_text.grid(column=2, row=1, sticky='we', padx=(45, 0))
        self.temp_text = tk.Label(
        self.temp_text, text='Temperatura (°C)', background='white')
        self.temp_text.pack(side='bottom', padx=(0, 5))
        
        self.var_temp = tk.Frame(self)
        self.var_temp.config(background='white')
        self.var_temp.grid(column=2, row=2, sticky='we', padx=(45, 0))
        self.int_temp = tk.IntVar(self.var_temp,27)
        self.text_label = tk.Label(
        self.var_temp, textvariable=self.int_temp, background='white')
        self.text_label.pack(side='bottom', padx=(0, 5))

def serial_ports():
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

if __name__ == "__main__":
    app = App()
    app.mainloop()