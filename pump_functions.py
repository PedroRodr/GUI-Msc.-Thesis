import math, time, scipy
from board_functions import *
from PyQt5.QtCore import QThread, pyqtSignal

# Thread that reads in real-time the pump position
class pump_read(QThread):
    
    # Signal to update the label position, and pump state
    position_state_updated = pyqtSignal(float, str)  

    def __init__(self, serial_connection_pump):
        super().__init__()
        
        self.serial_connection_pump = serial_connection_pump                                                    # Pump serial port
        self.running = True

    def run(self):
        
        try:
            counter = 0
            while self.running:
                
                get_pump_pos = "?\r\n"
                self.serial_connection_pump.write(get_pump_pos.encode())                                        # Send position request
                time.sleep(0.2)
                response =  self.serial_connection_pump.read( self.serial_connection_pump.in_waiting or 1)
                
                if counter != 0:
                    parts = response.decode()
                    pump_state = parts[1]                                   
                    pump_pos = parts.split('|')[1].split(':')[1].split(',')[0]
                    
                    # If pump state is Idle or Hold stop thread
                    if pump_state == "I" or pump_state == "H":
                        self.running = False
                        self.position_state_updated.emit(float(pump_pos),pump_state)                            # Emit new pump position to function update_pump_pos
                        break

                    self.position_state_updated.emit(float(pump_pos),pump_state)                                # Emit new pump position to function update_pump_pos

                counter = counter + 1

        except Exception as e:
            print("Error:", e)

    def stop(self):
        self.running = False
        self.wait() 


# Function to start the thread
def start_tracking_pump_pos(self):
    
    if self.read_pump_thread is None or not self.read_pump_thread.isRunning():
        self.read_pump_thread = pump_read(self.serial_connection_pump)
        self.read_pump_thread.position_state_updated.connect(lambda pump_pos, pump_state: update_pump_pos(self, pump_pos, pump_state))
        self.read_pump_thread.start()


# Function to stop the thread
def stop_tracking_pump_pos(self, pump_state):
    
    # Stop tracking pump thread
    if self.read_pump_thread and self.read_pump_thread.isRunning():
        self.read_pump_thread.stop()
        self.read_pump_thread = None

    # Stop read data thread
    if  self.ui.pump_acq_data.isChecked() and (pump_state == "I" or pump_state == "H"):
        self.ui.pump_acq_data.setEnabled(True)
        self.data_thread.stop()
        self.data_thread = None
        scipy.io.savemat("mw_board_data.mat", {"mw_board_data": self.y_values})
    
    


# Function to update the label with the new pump position
def update_pump_pos(self, pump_pos, pump_state):    
    
    self.ui.liquid_out_read.setText(f"{abs(pump_pos):.3f}")
    
    # If pump state is Idle or Hold stop thread
    if pump_state == "I" or pump_state == "H":
        self.ui.liquid_out_read.setText(f"{0:.3f}")
        stop_tracking_pump_pos(self, pump_state)


# Init pump. The while loop waits for the arduino answer. 
# Connection is accomplished when the arduino sends the string "help".
def pump_init(self):

    error_conect = 0
    exit_counter = 0
    help_str = 1
    
    while help_str:
        
        self.serial_connection_pump.write("\r".encode())
        time.sleep(0.1)
        response = self.serial_connection_pump.read(self.serial_connection_pump.in_waiting or 1)
        help_str = 0 if b"help" in response else 1
        
        # Could not connect to arduino.
        if exit_counter > 5:
            error_conect = 1
            return error_conect
        exit_counter = exit_counter + 1
    
    # Pump_defs programs the steps per ml.
    pump_defs(self)
    sent_code = "G92 X0\r\n"
    self.serial_connection_pump.write(sent_code.encode())
    return error_conect


# Sets the value for steps per ml. Always programmed intially.    
def pump_defs(self):

    pump_stp_ang = float(self.ui.pump_stp_ang.text())
    pump_stp_driver = float(self.ui.pump_stp_driver.text())
    pump_leadscrew = float(self.ui.pump_leadscrew.text())
    pump_syr_diam = float(self.ui.pump_syr_diam.text())

    min_mov = pump_leadscrew / ((360/pump_stp_ang) * pump_stp_driver)
    volume_per_mm = (pow((pump_syr_diam/2),2)*math.pi)/1000
    steps_per_ml = (1 / (volume_per_mm * min_mov))
    steps_per_ml = str(round(steps_per_ml))
    #print(steps_per_ml)
    
    code_steps_per_ml = "$100="
    first_msg_string = "{}{}{}".format(code_steps_per_ml, steps_per_ml,"\r\n")                                 # Program steps per ml        
    self.serial_connection_pump.write(first_msg_string.encode())
    time.sleep(0.1)
    
    # TODO: Bug when stop button is pressed, after programming the pump. The pump only works correctly at the second time.
    # Dummy movement to solve TODO task.
    sent_code = "G91G1X0.01F50\r\n"
    self.serial_connection_pump.write(sent_code.encode())
    time.sleep(0.1)
    
    aux = "?\r\n"
    self.serial_connection_pump.write(aux.encode())                                                            # Send position request
    time.sleep(0.1)
    

# Move pump foward or backwards. Needs liquid to pump out, and flux value.
def pump_move(self, device):

    pump_liquid_out = (self.ui.pump_liquid_out.text())
    pump_flux = (self.ui.pump_flux.text())
    set_liquidout_flux_code = "{}F{}".format(pump_liquid_out,pump_flux)

    if device == "Foward":
        sent_code = "G91G1X-{}\r\n".format(set_liquidout_flux_code)
        self.serial_connection_pump.write(sent_code.encode())
        #print("sent_code=",sent_code)
    elif device == "Backward":
        sent_code = "G91G1X{}\r\n".format(set_liquidout_flux_code)
        self.serial_connection_pump.write(sent_code.encode())
        #print("sent_code=",sent_code)
    
    sent_code = "G92 X0\r\n"
    self.serial_connection_pump.write(sent_code.encode())
    #time.sleep(0.1)
    start_tracking_pump_pos(self)
    if  self.ui.pump_acq_data.isChecked():
        self.ui.pump_acq_data.setEnabled(False)
        read_board_data(self, 1)

# Stop pump from moving
def stop_pump(self):

    unlock_grbl = "!\r\n"                                                                                      # Stop motion
    self.serial_connection_pump.write(unlock_grbl.encode())
    time.sleep(0.2)
    stop_code = b'\x18\r\n'                                                                                    # Reset pump
    self.serial_connection_pump.write(stop_code)
    time.sleep(0.2)
    unlock_grbl = "$X\r\n"                                                                                     # Unlock GRBL
    self.serial_connection_pump.write(unlock_grbl.encode())
    time.sleep(0.2)
    response = self.serial_connection_pump.read( self.serial_connection_pump.in_waiting or 1)
    time.sleep(0.2)