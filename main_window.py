from PySide6.QtWidgets import (
    QMainWindow, QStatusBar, QToolBar, QLabel, QWidget, QHBoxLayout,
    QSizePolicy
)
from PySide6.QtGui import QAction
from PySide6.QtCore import QSize, Qt
# module viewer_widget
from viewer_widget import ViewerWidget
from controls_panel import ControlsPanel



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Underwater GPS")
        self.resize(900, 700)
        
        #canvas:
        central_widget = QWidget()
        layout = QHBoxLayout()
        

        
        ## ViewerWidget left side
        self.viewer = ViewerWidget()
        
        #For now left canvas only
        layout.addWidget(self.viewer, 2)
        
        # show layout before toolbar and menu
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        #controls_panel
        self.controls_panel = ControlsPanel()
        layout.addWidget(self.controls_panel, 1)
        
        # Toolbar (now only empty or used for other actions if needed like stop[])
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # Status bar
        self.setStatusBar(QStatusBar(self))

        # Menu bar - File
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        
        #Menu bar - View
        view_menu = menu.addMenu("&View")
        
        #Menu bar - Tools
        tool_menu = menu.addMenu("&Tools")
        
        # Menu bar - About 

        about_menu = menu.addMenu("&About")
        

        # Save submenu under File
        save_menu = file_menu.addMenu("Save")
        
        file_menu.addSeparator()
        
        # Print Screenshot under File
        print_screen = file_menu.addAction("Print Screenshot")

        # Save to CSV action
        save_csv_action = QAction("Save to CSV", self)
        save_csv_action.setCheckable(True)
        save_csv_action.triggered.connect(self.save_action_csv)
        save_menu.addAction(save_csv_action)
        
        # Save to json action
        save_json_action = QAction("save to JSON File", self)
        save_json_action.setCheckable(True)
        save_json_action.triggered.connect(self.save_action_json)
        save_menu.addAction(save_json_action)
        
        #Load simulation button - File
        file_menu.addSeparator()
        load_recorded_data = file_menu.addAction("Load Recorded Data")
        

        # Exit action
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        

        # End of File menu
        
        #sub menu for view 
        
        # view submenu - Show Depth reading button
        dept_reading = view_menu.addMenu("Show Depth Readings")
        
        view_menu.addSeparator()
        # Reset view button from other options 
        reset_view = view_menu.addMenu("Reset View")
        
        # end of submenu for view
        
        #sub menu for tools
        
        # button for real time tracking
        start_real_time_tracking = tool_menu.addMenu("Start Real-Time Tracking")


    def save_action(self, checked):
        print("Save Data clicked:", checked)
        
    def save_action_csv(self, checked):
        print("Save to CSV clicked:", checked)
        
    def save_action_json(self, checked):
        print("Save to json file:", checked)
        