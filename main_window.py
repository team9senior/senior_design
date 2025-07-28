from PySide6.QtWidgets import (
    QMainWindow, QStatusBar, QToolBar, QLabel, QWidget, QHBoxLayout,
    QSizePolicy, QMessageBox
)
from PySide6.QtGui import QAction
from PySide6.QtCore import QSize, Qt, QThread, Signal, QTimer # Added QThread, Signal, QTimer
import numpy as np # Import numpy for mathematical functions like arcsin
import serial # Import pyserial for serial communication
from viewer_widget import ViewerWidget
from controls_panel import ControlsPanel


# --- Serial Reader Class ---
class SerialReader(QThread):
    data_received = Signal(float)
    error_occurred = Signal(str)

    def __init__(self, port, baud_rate):
        super().__init__()
        self.port = port
        self.baud_rate = baud_rate
        self.running = False
        self.serial_connection = None

    def run(self):
        self.running = True
        try:
            self.serial_connection = serial.Serial(self.port, self.baud_rate, timeout=1)
            print(f"Connected to serial port {self.port} at {self.baud_rate} baud.")
            self.error_occurred.emit(f"Connected to {self.port}") # Confirm connection in status bar
            while self.running:
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    try:
                        delta_t = float(line)
                        self.data_received.emit(delta_t)
                    except ValueError:
                        print(f"Could not parse '{line}' as float. Skipping.")
                self.msleep(10)
        except serial.SerialException as e:
            self.error_occurred.emit(f"Serial port error: {e}. Check port settings and connection.")
            print(f"Serial port error: {e}")
        except Exception as e:
            self.error_occurred.emit(f"An unexpected error occurred in serial reader: {e}")
            print(f"An unexpected error occurred: {e}")
        finally:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
            print("Serial reader stopped.")


class MainWindow(QMainWindow):
    # Fixed parameters for the TDOA calculation (no longer user inputs)
    DEFAULT_MIC_DISTANCE = 0.0762    # meters (3 inches)
    DEFAULT_SPEED_OF_SOUND = 1500.0 # m/s (e.g., speed in water)
    BAUD_RATE = 115200 # Match your ESP32's baud rate

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Underwater GPS (ESP32 Live Data)")
        self.resize(900, 700)

        # Layout for GUI
        central_widget = QWidget()
        layout = QHBoxLayout()

        ## ViewerWidget - The canvas for the compass display
        from viewer_widget import ViewerWidget # Local import to ensure it's available
        self.viewer = ViewerWidget()
        layout.addWidget(self.viewer, 2)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # controls_panel - right side
        from controls_panel import ControlsPanel # Local import
        self.controls_panel = ControlsPanel()
        layout.addWidget(self.controls_panel, 1)

        # Initialize SerialReader related attributes
        self.serial_reader = None
        self.current_com_port = self.controls_panel.port_input.text() # Get initial port from GUI

        # Connect the COM port change signal from ControlsPanel
        self.controls_panel.com_port_changed.connect(self._update_com_port)

        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # Status bar
        self.setStatusBar(QStatusBar(self))

        # --- Menu Bar Setup ---
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        view_menu = menu_bar.addMenu("View")
        tool_menu = menu_bar.addMenu("Tools")
        help_menu = menu_bar.addMenu("Help")

        # Start Real-Time Tracking Action
        self.start_tracking_action = QAction("Start Real-Time Tracking", self)
        self.start_tracking_action.triggered.connect(self._start_serial_tracking)
        tool_menu.addAction(self.start_tracking_action)

        # Stop Real-Time Tracking Action
        self.stop_tracking_action = QAction("Stop Real-Time Tracking", self)
        self.stop_tracking_action.triggered.connect(self._stop_serial_tracking)
        self.stop_tracking_action.setEnabled(False) # Disable until tracking starts
        tool_menu.addAction(self.stop_tracking_action)

        # Exit action
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Placeholder menu actions (from previous versions, kept for completeness)
        save_menu = file_menu.addMenu("Save Data")
        save_csv_action = QAction("Save to CSV File", self)
        save_csv_action.triggered.connect(self.save_action_csv)
        save_menu.addAction(save_csv_action)
        save_json_action = QAction("save to JSON File", self)
        save_json_action.triggered.connect(self.save_json_action)
        save_menu.addAction(save_json_action)
        load_recorded_data = file_menu.addAction("Load Recorded Data")
        dept_reading = view_menu.addMenu("Show Depth Readings")
        reset_view = view_menu.addMenu("Reset View")


    def _update_com_port(self, new_port_str):
        """Updates the COM port to be used for serial communication."""
        if self.serial_reader and self.serial_reader.isRunning():
            QMessageBox.information(self, "Port Change",
                                    "Please stop real-time tracking before changing the COM port. "
                                    "Restart tracking for the new port to take effect.")
            # Revert the input field to the currently active port if tracking is running
            self.controls_panel.port_input.setText(self.current_com_port)
        else:
            self.current_com_port = new_port_str
            self.statusBar().showMessage(f"COM Port updated to: {self.current_com_port}")


    def _start_serial_tracking(self):
        """Initializes and starts the serial reader thread."""
        if not self.current_com_port:
            QMessageBox.warning(self, "COM Port Missing", "Please enter a COM Port in the Serial Settings.")
            return

        if self.serial_reader is None or not self.serial_reader.isRunning():
            self.serial_reader = SerialReader(self.current_com_port, self.BAUD_RATE)
            self.serial_reader.data_received.connect(self._handle_live_delta_t)
            self.serial_reader.error_occurred.connect(self._show_serial_error)
            self.serial_reader.start()
            self.start_tracking_action.setEnabled(False)
            self.stop_tracking_action.setEnabled(True)
            self.statusBar().showMessage(f"Attempting to connect to {self.current_com_port}...")

    def _stop_serial_tracking(self):
        """Stops the serial reader thread and resets GUI state."""
        if self.serial_reader: # Check if a thread object exists at all
            if self.serial_reader.isRunning(): # If it's still running, actively stop it
                print("Attempting to stop active serial reader thread.") # Added for debugging
                self.serial_reader.stop() # This method tells the thread to finish
            else:
                print("Serial reader thread exists but is not running.") # Added for debugging
            # In any case (whether it was running or already finished due to an error),
            # clean up the reference to the thread object.
            self.serial_reader = None
        else:
            print("No serial reader thread instance found.") # Added for debugging

        # These lines should ALWAYS execute to reset the GUI state
        self.start_tracking_action.setEnabled(True)
        self.stop_tracking_action.setEnabled(False)
        self.statusBar().showMessage("Real-time tracking stopped.")

    def _handle_live_delta_t(self, delta_t):
        """Receives live delta_t from serial and triggers angle calculation."""
        self._calculate_and_display_angle(
            delta_t,
            self.DEFAULT_MIC_DISTANCE,
            self.DEFAULT_SPEED_OF_SOUND
        )
        # Status bar already updated by SerialReader on connection,
        # but can add delta_t update if desired:
        # self.statusBar().showMessage(f"Live Delta T: {delta_t:.6f}s")


    def _calculate_and_display_angle(self, delta_t, mic_distance, speed_of_sound):
        """Calculates the angle and updates the viewer widget."""
        try:
            if mic_distance == 0:
                print("Error: Microphone distance cannot be zero for angle calculation.")
                self.statusBar().showMessage("Error: Mic distance is zero!")
                return

            arg = (delta_t * speed_of_sound) / mic_distance
            
            # Clamp the argument to ensure it's within valid range for arcsin
            if arg > 1.0:
                arg = 1.0
            elif arg < -1.0:
                arg = -1.0

            angle_rad = np.arcsin(arg)
            angle_deg = np.degrees(angle_rad)

            print(f"Calculated Angle: {angle_deg:.2f}° (Live)")
            self.viewer.set_angle(angle_rad)

        except Exception as e:
            print(f"An error occurred during angle calculation: {e}")
            self.statusBar().showMessage(f"Calculation error: {e}")

    def _show_serial_error(self, message):
        QMessageBox.critical(self, "Serial Error", message)
        # No need to update status bar again, message box is primary notification
        self._stop_serial_tracking() # Attempt to stop tracking on error

    def closeEvent(self, event):
        """Ensure serial reader thread is stopped when the main window closes."""
        self._stop_serial_tracking()
        super().closeEvent(event)

    # --- Existing placeholder methods ---
    def save_action(self, checked):
        print("Save Data clicked:", checked)

    def save_action_csv(self, checked):
        print("Save to CSV File clicked:", checked)

    def save_json_action(self, checked):
        print("Save to JSON File clicked:", checked)