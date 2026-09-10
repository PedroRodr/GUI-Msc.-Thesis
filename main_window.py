import sys, serial, os
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox, QGraphicsView, QGraphicsItem, QVBoxLayout, QPushButton
from PyQt5 import QtGui,uic
from PyQt5.QtCore import Qt, QMutex, QSemaphore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from gui_gen import Ui_MainWindow 
from serial.tools import list_ports
import pyqtgraph as pg
import scipy.io
from pyqtgraph import PlotWidget

from CNC_functions import *
from board_functions import *

pg.setConfigOptions(useOpenGL=True)

base_dir = os.path.dirname(os.path.abspath(__file__))  
image_path = os.path.join(base_dir, "img", "pump_2.png") 

class MainWindow(QMainWindow):
    def __init__(self):
        
        super(MainWindow, self).__init__()
        #uic.loadUi('gui_gen.ui', self)  # Save your Qt Designer file with this name
        self.ui = Ui_MainWindow()                                                                                   
        self.ui.setupUi(self)   

                                                                                       

        # Initializations.
        self.initializations()

        # Initialize controls for the COM ports.
        self.ui.board_coms_refresh.clicked.connect(lambda: self.update_com_ports("Board"))
        
        # Connect / disconnect board.
        self.ui.board_connect.clicked.connect(lambda: self.show_controls("Board"))
        self.ui.board_disc.clicked.connect(lambda: self.show_com_ports("Board"))

        # MW board controls.
         
        # Only read data from mw board, without moving the pump.
        # The reading data from mw board is in a thread, so that it can update the data in real time in the chart.
        self.ui.board_read_data.clicked.connect(lambda: read_board_data_probe(self))            
        self.ui.debug_mode.clicked.connect(lambda: debug_mode(self))           
        self.ui.debug_save.clicked.connect(lambda: save_debug_mat_file(self))
        self.clear_plot_btn.clicked.connect(self.clear_plot) 

    # Read avaible COM ports, and update the COM ports in a list.
    def update_com_ports(self, device):
        
        ports = serial.tools.list_ports.comports()
        if device == "Board":
            self.ui.board_coms_list.clear()
            for port in sorted(ports):
                self.ui.board_coms_list.addItem(port.device)
        elif device == "CNC":
            self.ui.cnc_coms_list.clear()
            for port in sorted(ports):
                self.ui.cnc_coms_list.addItem(port.device)


    # Show the board or pump controls
    def show_controls(self, device):
        
        # Try to connect to the mw board. If it connects shows controls.
        if device == "Board":
            selected_port = self.ui.board_coms_list.currentText()
            if selected_port:
                try:
                    self.serial_connection_board = serial.Serial(selected_port, baudrate=115200, timeout=10)
                    self.ui.board_stacked_widget.setCurrentIndex(1)
                    get_id(self)
                    #init_program_mw_board(self)                                                                     # Program with initial values the mw board.                        
                
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to connect to {selected_port}: {e}")
            else:
                QMessageBox.warning(self, "Warning", "No COM port selected")
        
        # Try to connect to the pump. If it connects shows controls.      
        elif device == "CNC":
            selected_port = self.ui.cnc_coms_list.currentText()
            if selected_port:
                try:
                    self.serial_connection_cnc = serial.Serial(selected_port, baudrate=115200, timeout=1)
                    error_conect = cnc_init(self)
                    if error_conect == 0:
                        self.ui.pump_stacked_widget.setCurrentIndex(1)
                    else:
                        self.show_com_ports("CNC")
                        QMessageBox.critical(self, "Error", f"Connected to {selected_port}, but failed to connect to Arduino")
                
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to connect to {selected_port}: {e}")
            else:
                QMessageBox.warning(self, "Warning", "No COM port selected")
    

    # When disconnect board or pump, go back to the main menu to choose the COM port again.
    def show_com_ports(self, device):
        
        if device == "Board":
            self.serial_connection_board.close()
            self.serial_connection_board = None
            self.ui.board_stacked_widget.setCurrentIndex(0)
            self.ui.cnc_acq_data.setChecked(True)
            self.timer.stop()
        elif device == "CNC":
            self.serial_connection_cnc.close()
            self.serial_connection_cnc = None
            self.ui.pump_stacked_widget.setCurrentIndex(0)


    def initializations(self):

        # Hide CNC panel and unused page switchers.
        self.ui.pump_stacked_widget.hide()
        self.ui.next_page.hide()
        self.ui.previous_page.hide()
        self.ui.board_en_output_write_2.hide()

        # Align left board panel and right plot to the same top/height.
        self.ui.board_stacked_widget.setGeometry(0, 0, 460, 880)
        self.ui.heatmapStackedWidget.setGeometry(460, 0, 850, 880)

        # Vertically center board COM controls in the left panel.
        self.ui.board_coms_list.setGeometry(150, 363, 145, 35)
        self.ui.board_coms_refresh.setGeometry(150, 423, 145, 35)
        self.ui.board_connect.setGeometry(150, 483, 145, 35)

        # Vertically center board controls (channels / debug) when connected.
        
        self.ui.frame.setGeometry(20, 255, 400, 311)

        # Align bottom action buttons: same size, y, and spacing.
        btn_y, btn_w, btn_h, btn_gap = 590, 95, 35, 10
        btn_xs = [25, 25 + (btn_w + btn_gap), 25 + 2 * (btn_w + btn_gap), 25 + 3 * (btn_w + btn_gap)]
        shared_btn_style = """
QPushButton {
    border-radius: 8px;
    padding: 4px 8px;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #5E81AC;
}
QPushButton:pressed {
    background-color: #88C0D0;
}
"""
        self.ui.debug_mode.setGeometry(btn_xs[0], btn_y, btn_w, btn_h)
        self.ui.debug_mode.setStyleSheet(shared_btn_style + """
QPushButton { background-color: green; color: white; }
""")
        self.ui.debug_save.setGeometry(btn_xs[1], btn_y, btn_w, btn_h)
        self.ui.debug_save.setStyleSheet(shared_btn_style + """
QPushButton { background-color: red; color: white; }
""")

        self.clear_plot_btn = QPushButton("Clear", self.ui.board_controls)
        self.clear_plot_btn.setGeometry(btn_xs[2], btn_y, btn_w, btn_h)
        self.clear_plot_btn.setStyleSheet(shared_btn_style + """
QPushButton { background-color: #4C566A; color: #ECEFF4; }
""")
        self.clear_plot_btn.show()

        self.ui.board_disc.setGeometry(btn_xs[3], btn_y, btn_w, btn_h)
        self.ui.board_disc.setStyleSheet(shared_btn_style + """
QPushButton { background-color: #4C566A; color: #ECEFF4; }
""")

        #self.ui.label_5.setPixmap(QtGui.QPixmap(image_path))                                                        # Set pump image.  
        #self.ui.label_5.setScaledContents(True)                                                                     # Set pump image.
        self.heatmap_canvas = MplGraph(self.ui.heatmapWidget, width=8 , height=8, dpi=100)                                                                               # Initialize chart layout.
        self.debug_canvas = MplGraph(self.ui.debugWidget, width=8 , height=8, dpi=100)                                                                                   # Initialize debug chart layout.
        self.debug_canvas2 = MplGraph(self.ui.debugWidget2, width=8 , height=8, dpi=100)  
        self.fig = Figure(figsize=(5, 4), dpi=100)                                              # If button pressed, clear data.
        self.axes = self.fig.add_subplot(111)
        self.data_matrix = []                                                                                          # Init data matrix to store data read from mw board.
        self.xlabel = []                                                                                          # Init x array for chart.
        self.ylabel = []                                                                                          # Init Y array for chart.
        
        self.serial_connection_board = None                                                                         # COM port for the board.                            
        self.serial_connection_cnc = None                                                                          # COM port for the pump.
        
        self.cnc_read = None                                                                                     # Theread for read data from MW board and plot it.
        self.read_cnc_thread = None                                                                                # Theread to read pump position.
 
        # Align output labels to the center                                                       
        self.ui.board_ch0_read.setAlignment(Qt.AlignCenter) 
        self.ui.board_ch1_read.setAlignment(Qt.AlignCenter)
        self.ui.board_ch2_read.setAlignment(Qt.AlignCenter)
        self.ui.board_ch3_read.setAlignment(Qt.AlignCenter)
        self.ui.board_ch4_read.setAlignment(Qt.AlignCenter)
        self.ui.board_ch5_read.setAlignment(Qt.AlignCenter)                                                     
        self.ui.board_id_read.setAlignment(Qt.AlignCenter)                                                                                                                                        
                                                            
    def read_matrix(self):
        return self.read_cnc_thread.get_matrix()


    # Update the plot with new data.
    def update_plot(self):
        self.ui.cnc_acq_data.setChecked(False)
        self.data_matrix,self.data_res_x, self.data_res_y = self.read_cnc_thread.get_matrix()
        
        # Create heatmap
        #print("Dados a serem adicionados: ", self.data_matrix)
        print("Shape of matrix: ", np.shape(self.data_matrix))
        print("Max value: ", np.max(self.data_matrix))
        print("Min value: ", np.min(self.data_matrix))
        self.heatmap_canvas.plot_heatmap(self.data_matrix,self.data_res_x, self.data_res_y, title="Sensor Data")

    def plot1D_debug(self):
        #self.ui.heatmapStackedWidget.setCurrentIndex(1)
        self.realtime.append(read_board_data_probe(self)[0])
        #x_even = self.realtime[::2]  # Select every second element
        #x_odd = self.realtime[1::2]  # Select every second element starting from the second
        #self.debug_canvas.plot1D(x_even, title="Real-time Data - Even Channels")
        #self.debug_canvas2.plot1D(x_odd, title="Real-time Data - Odd Channels")
        self.debug_canvas2.plot1D(self.realtime, title="Real-time Data - All Channels")

    def clear_plot(self):
        self.realtime = []
        self.debug_canvas2.axes.clear()
        self.debug_canvas2.axes.set_xlabel('X Axis')
        self.debug_canvas2.axes.xaxis.label.set_color('#88C0D0')
        self.debug_canvas2.axes.set_ylabel('Y Axis')
        self.debug_canvas2.axes.yaxis.label.set_color('#88C0D0')
        self.debug_canvas2.axes.set_title("Real-time Data - All Channels")
        self.debug_canvas2.axes.title.set_color('#D8DEE9')
        self.debug_canvas2.draw()

class MplGraph(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#2E3440')  # Set background color to match dark theme
        self.fig.patch.set_facecolor('#2E3440')  # Set figure background color
        self.axes.set_xlabel('X Axis')
        self.axes.xaxis.label.set_color('#88C0D0')  # Set x-axis label color
        self.axes.set_ylabel('Y Axis')
        self.axes.yaxis.label.set_color('#88C0D0')  # Set y-axis label color
        self.axes.tick_params(axis='x', colors='#D8DEE9')  # Set x-axis tick color
        self.axes.tick_params(axis='y', colors='#D8DEE9')  # Set y-axis tick color
        self.axes.spines['bottom'].set_color('#D8DEE9')  # Set bottom spine color
        self.axes.spines['top'].set_color('#D8DEE9')     # Set top spine color
        self.axes.spines['left'].set_color('#D8DEE9')    # Set left spine color
        self.axes.spines['right'].set_color('#D8DEE9')   # Set right spine color
        self.colorbar = None

    def plot_heatmap(self, data, x_step=None, y_step=None, title="Heatmap"):
        """Plot heatmap with proper axis labels"""
        self.axes.clear()

        # Create heatmap
        im = self.axes.imshow(data, cmap='jet', aspect='auto')
        
        # Set axis labels
        x_label = np.arange(len(data[0]))*x_step/8  
        #self.axes.set_xticks(range(len(x_label)), labels= x_label)
        self.axes.set_xlabel('X Axis Values [samples]')
        self.axes.xaxis.label.set_color('#88C0D0')  # Set x-axis label color

        y_label = np.arange(len(data))*y_step
        #print("Y LABEL: ", y_label)
        #self.axes.set_yticks(range(len(y_label)), labels = y_label)
        self.axes.set_ylabel('Y Axis Values [samples]')
        self.axes.yaxis.label.set_color('#88C0D0')  # Set y-axis label color
        
        # Add colorbar and title
        
        self.axes.colorbar = self.fig.colorbar(im, ax=self.axes, label='Intensity')
        self.axes.colorbar.ax.yaxis.label.set_color('#D8DEE9')  # Set colorbar label color
        self.axes.colorbar.ax.yaxis.set_tick_params(color='#D8DEE9')  # Set colorbar tick color
        self.axes.colorbar.outline.set_edgecolor('#D8DEE9')  # Set colorbar outline color
        self.axes.colorbar.ax.tick_params(axis='y', colors='#D8DEE9', labelsize=9)
    
        self.axes.set_title(title)
        self.axes.title.set_color('#D8DEE9')  # Set title color
        
        # Adjust layout to prevent label cutting
        self.fig.tight_layout()
        self.draw()
        self.axes.colorbar.remove()  # Remove colorbar to prevent multiple colorbars on update
    def plot1D(self, x, title="1D Plot"):
        self.axes.clear()
        self.x_1 = x[::3]  # Select every third element
        #self.x_2 = x[1::3]  # Select every third element starting from the second
        #3self.x_3 = x[2::3]  # Select every third element starting from the third
        self.axes.plot(self.x_1, color='c', label='Channel 1')
        #self.axes.plot(self.x_2, color='m', label='Channel 2')
        #self.axes.plot(self.x_3, color='y', label='Channel 3')
        self.axes.set_xlabel('X Axis')
        self.axes.xaxis.label.set_color('#88C0D0')  # Set x-axis label color
        self.axes.set_ylabel('Y Axis')
        self.axes.yaxis.label.set_color('#88C0D0')  # Set y-axis label color
        self.axes.set_title(title)
        self.axes.title.set_color('#D8DEE9')  # Set title color
        self.axes.legend()
        self.draw()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)                                                                                    # Create the application.
    window = MainWindow()                                                                                           # Create an instance of your main window.
    window.show()                                                                                                   # Show the main window.
    sys.exit(app.exec_())                                                                                           # Start the event loop.