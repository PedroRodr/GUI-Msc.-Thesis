import math, time, scipy
from board_functions import *
from PyQt5.QtCore import QThread, pyqtSignal
from main_window import MplGraph

# Thread that reads in real-time the cnc position
class cnc_read(QThread):
    
    array_to_plot = pyqtSignal(object)
    finished_signal = pyqtSignal()  

    def __init__(self, serial_connection_cnc,serial_connection_board,ui,cnc_x_res,cnc_y_res,cnc_x_span,cnc_y_span,Direction_Y,Direction_X,heatmap_canvas):
        super().__init__()
        self.heatmap_canvas = heatmap_canvas
        self.serial_connection_cnc = serial_connection_cnc                                                    # cnc serial port
        self.serial_connection_board = serial_connection_board 
        self.ui = ui
        self.cnc_x_res = cnc_x_res
        self.cnc_y_res = cnc_y_res
        self.cnc_x_span = cnc_x_span
        self.cnc_y_span = cnc_y_span
        self.Direction_Y = Direction_Y
        self.Direction_X = Direction_X
        self.x_steps = int(cnc_x_span / cnc_x_res)
        self.y_steps = int(cnc_y_span / cnc_y_res)
        self.data_list = []
        self.data_point = [] 
        self.data_row = []
        self.data_matrix = [[0 for _ in range(self.x_steps*N_CHANNELS)] for _ in range(self.y_steps)]  # Initialize empty data matrix, multiplica x_steps por 8 pelo numero de sensores
        #Defining the sent codes based on the direction selected
        if Direction_X:
            self.sent_codex_res = "G91G0X-{}\r\n".format(cnc_x_res)
            self.sent_codex_span = "G91G0X{}\r\n".format(cnc_x_span)
        else:
            self.sent_codex_res = "G91G0X{}\r\n".format(cnc_x_res)
            self.sent_codex_span = "G91G0X-{}\r\n".format(cnc_x_span)
        if Direction_Y:
            self.sent_codey_res = "G91G0Y{}\r\n".format(cnc_y_res)
            self.sent_codey_span = "G91G0Y-{}\r\n".format(cnc_y_span)
        else:
            self.sent_codey_res = "G91G0Y-{}\r\n".format(cnc_y_res)
            self.sent_codey_span = "G91G0Y{}\r\n".format(cnc_y_span)
        self.running = True
    def run(self):
        
        try:
            counter = 0
            while self.running:
                get_cnc_pos = "?\r\n"
                self.serial_connection_cnc.write(get_cnc_pos.encode())                                        # Send position request
                time.sleep(0.2)
                response =  self.serial_connection_cnc.read( self.serial_connection_cnc.in_waiting or 1)

                if counter != 0:
                    parts = response.decode()
                    cnc_state = parts[1]                                   
                    
                    # If cnc state is Idle or Hold stop thread
                    if cnc_state == "I" or cnc_state == "H":
                        self.running = False
                        for j in range(self.x_steps): 
                            for i in range(self.y_steps):
                                self.data_row = read_board_data_probe(self)           # Read data from board
                                print("Len Data: ",len(self.data_row))
                                self.serial_connection_cnc.write(self.sent_codey_res.encode())
                                for k in range (0,N_CHANNELS) :  # Repeat for 8     sensors
                                    self.data_matrix [i][j*N_CHANNELS+k]=(self.data_row[k])              # Append the row to the matrix
                                self.wait_cnc()
                            self.serial_connection_cnc.write(self.sent_codey_span.encode())
                            self.wait_cnc()
                            #time.sleep(8)
                            self.serial_connection_cnc.write(self.sent_codex_res.encode())
                            self.wait_cnc()
                            #time.sleep(1)
                            self.data_row = []                                  # Clear the row for the next iteration
                        print("Data matrix collected:",self.data_matrix)
                        # Return to the original position
                        self.serial_connection_cnc.write(self.sent_codex_span.encode())
                        self.array_to_plot.emit(self.data_matrix)
                        self.finished_signal.emit() 
                        #self.data_thread.new_point_signal.connect(self.unpack_data_thread.unpack_data_read, Qt.ConnectionType.QueuedConnection)
                        break

                counter = counter + 1

        except Exception as e:
            print("Error CNC thread:", e)

    def get_matrix(self):
        return self.data_matrix,self.cnc_x_res,self.cnc_y_res 
    
    def wait_cnc(self):
        get_cnc_pos = "?\r\n"
        self.serial_connection_cnc.write(get_cnc_pos.encode())                                        # Send position request
        time.sleep(0.1)
        response =  self.serial_connection_cnc.read( self.serial_connection_cnc.in_waiting or 1)
        parts = response.decode()
        cnc_state = parts[1]
        while cnc_state != "I":
            self.serial_connection_cnc.write(get_cnc_pos.encode())                                        # Send position request
            time.sleep(0.1)
            response =  self.serial_connection_cnc.read( self.serial_connection_cnc.in_waiting or 1)
            parts = response.decode()
            cnc_state = parts[1]
        time.sleep(0.1)
    

# Function to start the thread
def start_tracking_cnc_pos(self,cnc_x_res,cnc_y_res,cnc_x_span,cnc_y_span,Direction_Y,Direction_X):
    
    if self.read_cnc_thread is None or not self.read_cnc_thread.isRunning():
        self.read_cnc_thread = cnc_read(self.serial_connection_cnc,self.serial_connection_board,self.ui,cnc_x_res,cnc_y_res,cnc_x_span,cnc_y_span,Direction_Y,Direction_X,self.heatmap_canvas)
               
        # Connect data_thread to unpack_data_thread.
        self.read_cnc_thread.array_to_plot.connect(self.read_cnc_thread.get_matrix, Qt.ConnectionType.QueuedConnection)                 
        # Signaling if thread ended without pressing the stop button.
        self.read_cnc_thread.finished_signal.connect(lambda: on_thread_finished(self))
        
        self.read_cnc_thread.start()
    

# Init cnc. The while loop waits for the arduino answer. 
# Connection is accomplished when the arduino sends the string "help".
def cnc_init(self):

    error_conect = 0
    exit_counter = 0
    help_str = 1
    while help_str:
        
        self.serial_connection_cnc.write("\r".encode())
        time.sleep(0.1)
        response = self.serial_connection_cnc.read(self.serial_connection_cnc.in_waiting or 1)
        help_str = 0 if b"help" in response else 1
        
        # Could not connect to arduino.
        if exit_counter > 5:
            error_conect = 1
            return error_conect
        exit_counter = exit_counter + 1
    
    # cnc_defs programs the steps per ml.
    cnc_defs(self)
    sent_code = "G92 X0\r\n"
    self.serial_connection_cnc.write(sent_code.encode())
    return error_conect


# Configure input for the CNC. Always programmed intially.    
def cnc_defs(self):

    config_file = open("1_config_xy_cnc.lvgs", "r")
    config_cmd = config_file.readlines()
    character = ";"             #Caracter to split the command from the comment
    for i in config_cmd:
        line = config_cmd[config_cmd.index(i)]
        data = line.split(character)
        data[0] = data[0] + '\n'
        data_to_send = data[0].encode('utf-8')
        self.serial_connection_cnc.write(data_to_send)
        time.sleep(0.1)
    config_file.close()
        

# Move cnc foward or backwards. Needs liquid to cnc out, and flux value.
def cnc_move(self, device):

    step_size = (self.ui.step_size.text())

    if device == "Left":
        sent_code = "G91G0X-{}\r\n".format(step_size)
        self.serial_connection_cnc.write(sent_code.encode())
        #print("sent_code=",sent_code)
    elif device == "Right":
        sent_code = "G91G0X{}\r\n".format(step_size)
        self.serial_connection_cnc.write(sent_code.encode())
        #print("sent_code=",sent_code)
    elif device == "Up":
        sent_code = "G91G0Y-{}\r\n".format(step_size)
        self.serial_connection_cnc.write(sent_code.encode())
        #print("sent_code=",sent_code)
    elif device == "Down":
        sent_code = "G91G0Y{}\r\n".format(step_size)
        self.serial_connection_cnc.write(sent_code.encode())
        #print("sent_code=",sent_code)
    
    sent_code = "G92 X0\r\n"
    self.serial_connection_cnc.write(sent_code.encode())
    #time.sleep(0.1)

#Called when the thread finishes after predefined iterations (ex: 50 iterations).
def on_thread_finished(self):
    save_mat_file(self)
    self.update_plot()
    self.update_plot_thread = None
    self.data_thread = None                                                                                         # Reset thread
    #self.view_box.setMouseEnabled(x=True, y=True)                                                                   # Unlock data chart.

    reset_button_style(self)                                                                                        # Change the button color to green and set text to "Read Data".
    #scipy.io.savemat("mw_board_data.mat", {"mw_board_data": self.y_values})                                         # Save data to file.

# Stop cnc from moving
def stop_cnc(self):

    unlock_grbl = "!\r\n"                                                                                      # Stop motion
    self.serial_connection_cnc.write(unlock_grbl.encode())
    time.sleep(0.2)
    stop_code = b'\x18\r\n'                                                                                    # Reset cnc
    self.serial_connection_cnc.write(stop_code)
    time.sleep(0.2)
    unlock_grbl = "$X\r\n"                                                                                     # Unlock GRBL
    self.serial_connection_cnc.write(unlock_grbl.encode())
    time.sleep(0.2)
    response = self.serial_connection_cnc.read( self.serial_connection_cnc.in_waiting or 1)
    time.sleep(0.2)

# CNC Scan function
def cnc_scan(self):
    cnc_x_res = float(self.ui.cnc_x_res.text())
    cnc_y_res = float(self.ui.cnc_y_res.text())
    cnc_x_span = float(self.ui.cnc_x_span.text())
    cnc_y_span = float(self.ui.cnc_y_span.text())
    Direction_Y = float(self.ui.CheckBox_Direction_Y.isChecked())
    Direction_X = float(self.ui.CheckBox_Direction_X.isChecked())
    start_tracking_cnc_pos(self, cnc_x_res,cnc_y_res,cnc_x_span,cnc_y_span,Direction_Y,Direction_X)
