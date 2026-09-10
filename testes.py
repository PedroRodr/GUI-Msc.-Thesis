import sys
import numpy as np
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplHeatmap(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.axes = self.fig.add_subplot(111)
        
    def plot_heatmap(self, data, x_labels=None, y_labels=None, title="Heatmap"):
        """Plot heatmap with proper axis labels"""
        self.axes.clear()
        
        # Create heatmap
        im = self.axes.imshow(data, cmap='viridis', aspect='auto')
        
        # Set axis labels
        if x_labels is not None:
            self.axes.set_xticks(np.arange(len(x_labels)))
            self.axes.set_xticklabels(x_labels, rotation=45, ha='right')
            self.axes.set_xlabel('X Axis Values')
        else:
            self.axes.set_xlabel('X Axis')
            
        if y_labels is not None:
            self.axes.set_yticks(np.arange(len(y_labels)))
            self.axes.set_yticklabels(y_labels)
            self.axes.set_ylabel('Y Axis Values')
        else:
            self.axes.set_ylabel('Y Axis')
        
        # Add colorbar and title
        self.fig.colorbar(im, ax=self.axes, label='Intensity')
        self.axes.set_title(title)
        
        # Adjust layout to prevent label cutting
        self.fig.tight_layout()
        self.draw()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load the UI file created in Qt Designer
        uic.loadUi('gui_gen.ui', self)  # Save your Qt Designer file with this name
        
        # Set up the heatmap
        self.setup_heatmap()
        
        # Connect signals and generate initial data
        self.setup_connections()
        self.generate_sample_data()
        
    def setup_heatmap(self):
        """Initialize the heatmap in the container widget"""
        # Create layout for heatmap widget
        layout = QVBoxLayout()
        self.heatmapWidget.setLayout(layout)
        
        # Create matplotlib canvas
        self.heatmap_canvas = MplHeatmap(self.heatmapWidget, width=5, height=4, dpi=100)
        layout.addWidget(self.heatmap_canvas)
        
    def setup_connections(self):
        """Connect UI elements to functions"""
        # If you add buttons in Qt Designer, connect them here
        # Example: self.pushButton_update.clicked.connect(self.generate_sample_data)
        pass
        
    def generate_sample_data(self):
        """Generate and display sample heatmap data"""
        # Create sample data (6 rows x 8 columns)
        rows, cols = 6, 8
        data = np.random.rand(rows, cols)
        print(data)
        # Create custom axis labels
        x_labels = [f'Time_{i}' for i in range(cols)]
        y_labels = [f'Sensor_{i}' for i in range(rows)]
        
        # Update the UI labels (the ones you created in Qt Designer)
        #self.labelTitle.setText("Sensor Data Heatmap")
        #self.labelXAxis.setText("Time Intervals")
        #self.labelYAxis.setText("Sensor IDs")
        
        # Plot the heatmap
        self.heatmap_canvas.plot_heatmap(
            data, 
            x_labels=x_labels, 
            y_labels=y_labels, 
            title="Real-time Sensor Data"
        )

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())