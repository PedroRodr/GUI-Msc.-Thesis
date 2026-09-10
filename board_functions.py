import time, scipy
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer, QMutex
from PyQt5.QtWidgets import QMessageBox
from dataclasses import dataclass # Declaração da classe de comandos
import numpy as np

TERMINATION_CHAR      = 126                                                                                         # 0X7E

N_CHANNELS     = 8        # Number of channels in the probe                                                                                  # Number of channels
DATA_SIZE = 2*N_CHANNELS  # Size of data array in CommandDef

@dataclass
class CommandDef:
    function: int    # uint8_t
    value: int       # uint32_t  
    size: int        # uint8_t
    data: np.array # uint8_t[DATA_SIZE]
    crc: int         # uint8_t
    control: int     # uint8_t
    
    def __init__(self, function=0, value=0, size=0, data=None, crc=0, control=TERMINATION_CHAR):
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
    def from_bytes(data_bytes):
        """Parse received bytes back into CommandDef object"""
        if len(data_bytes) < 8:  # Minimum size: 1 + 4 + 1 + 1 + 1 = 8 bytes
            raise ValueError(f"Data too short: {len(data_bytes)} bytes")
        

        # Unpack the fixed-size fields
        function = data_bytes[0]
        value = int.from_bytes(data_bytes[1:5], 'little')
        size = data_bytes[5]     
        if size == 0x90:
           size = 2*N_CHANNELS    # Special case handling for size 0x90

        # Calculate expected total length
        expected_length = 6 + size   # 1+2+1+data_size+1+1
        if len(data_bytes) < expected_length:
            print("ERRO aqui, data_bytes:", data_bytes)
            raise ValueError(f"Data too short for size {size}, expected {expected_length} bytes. But got {len(data_bytes)} bytes.")
        
        # Extract data array
        data_start = 6
        data_end = 6 + size
        data_array = np.zeros(DATA_SIZE, dtype=np.uint8)
        received_data = list(data_bytes[data_start:data_end])
        data_array[:len(received_data)] = received_data
        
        
        return (function, value, size, data_array)
    
def read_board_data_probe(self):
    data_buffer = [0] * N_CHANNELS
    cmd = CommandDef(function=0x13, data=None, value=5, size=1)
    cmd.data[0] = 0x1A
    cmd.data[1] = 0x2B
    data_to_send = cmd.to_bytes()
    self.serial_connection_board.write(data_to_send)
    response = self.serial_connection_board.read(self.serial_connection_board.in_waiting or 1)
    print("Resposta recebida em bits: " + response.hex())
    rcv = CommandDef.from_bytes(response)
    print(f"Response: {rcv}")

    try:
        ch_val = (int(rcv[1]))*(8*(10**-12))/(2**24)-(4*10**-12)     # Convert to Farads
        widget = getattr(self.ui, f"board_ch{rcv[3][0]}_read", None)
        if widget is not None:
            widget.setText(str(round(ch_val*1e15,2))) # Display value in aF
        data_buffer[0] = ch_val
        return data_buffer
    except Exception as e:
        print("Error updating channel reads:", e)

        

def get_id(self):
    self.calibration_air = np.zeros(N_CHANNELS, dtype=np.uint8);
    self.calibration_metal = np.zeros(N_CHANNELS, dtype=np.uint8);
    cmd = CommandDef(function=0x38, data=None, value=100, size=1)
    cmd.data[0] = 0x1A
    cmd.data[1] = 0x2B
    cmd.data[15] = 0x3C
    data_to_send = cmd.to_bytes()
    self.serial_connection_board.write(data_to_send)
    time.sleep(0.2)
    response = self.serial_connection_board.read(self.serial_connection_board.in_waiting)  # Expect 32 bytes back
    rcv = CommandDef.from_bytes(response)
    self.ui.board_id_read.setText(str(rcv[1]))
    
# Change the button color to red and set text to "STOP".
def start_button_style(self):
    
        self.ui.board_read_data.setStyleSheet("""
        QPushButton {
            background-color: red;
            color: white;
            border-radius: 8px;
            padding: 6px 12px;
        }

        QPushButton:hover {
            background-color: #5E81AC;
        }

        QPushButton:pressed {
            background-color: #88C0D0;
        }
        """)
        self.ui.board_read_data.setText("STOP")

# Change the button color to green and set text to "Read Data".
def reset_button_style(self):
    
    self.ui.board_read_data.setStyleSheet("""
        QPushButton {
            background-color: green;
            color: white;
            border-radius: 8px;
            padding: 6px 12px;
        }

        QPushButton:hover {
            background-color: #5E81AC;
        }

        QPushButton:pressed {
            background-color: #88C0D0;
        }
    """)
    self.ui.board_read_data.setText("Read \nData")

def debug_mode(self):
    self.realtime = []
        # Update Chart every 100 ms.
    self.timer = QTimer()
    self.timer.setInterval(500) #ToDo: Se houver falhas na leitura aumentar o intervalo para  mais.                                                                               
    self.timer.timeout.connect(self.plot1D_debug)

    # Start timer and threads.
    self.timer.start()

def save_mat_file (self):
    self.data_matrix,self.cnc_x_res,self.cnc_y_res = self.read_matrix()
    scipy.io.savemat("Cap_board_data.mat", {"Cap_board_data": self.data_matrix,"Res_x": self.cnc_x_res,"Res_y": self.cnc_y_res })                                     # Save data to file.

def save_debug_mat_file (self):
    print("Saving debug data to .mat file...", self.realtime)
    scipy.io.savemat("Debug_data.mat", {"Debug_CH0": self.realtime[::6], "Debug_CH1": self.realtime[1::6], "Debug_CH2": self.realtime[2::6], "Debug_CH3": self.realtime[3::6], "Debug_CH4": self.realtime[4::6], "Debug_CH5": self.realtime[5::6]})                                     # Save data to file.