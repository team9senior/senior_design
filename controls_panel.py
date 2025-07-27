from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QSlider, QGroupBox,
    QHBoxLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Signal # Import Signal for custom events

class ControlsPanel(QWidget):
    # New signal to emit the desired COM port string
    com_port_changed = Signal(str)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Heading
        header = QLabel("Controls")
        header.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(header)

        # Coordinates Group (These are for display, not input)
        coord_group = QGroupBox("Coordinates")
        coord_layout = QVBoxLayout()

        self.x_label = QLabel("X: 0.00")
        self.y_label = QLabel("Y: 0.00")
        self.z_label = QLabel("Z: 0.00")

        for label in (self.x_label, self.y_label, self.z_label):
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            coord_layout.addWidget(label)
        coord_group.setLayout(coord_layout)
        layout.addWidget(coord_group)

        # --- New: Serial Settings Group ---
        serial_settings_group = QGroupBox("Serial Settings")
        serial_layout = QVBoxLayout()

        self.port_input = QLineEdit("COM3") # Default value, users can change this
        self.port_input.setPlaceholderText("e.g., COM3 or /dev/ttyUSB0")
        serial_layout.addWidget(QLabel("COM Port:"))
        serial_layout.addWidget(self.port_input)

        self.set_port_button = QPushButton("Set COM Port")
        serial_layout.addWidget(self.set_port_button)
        # Connect the button click to our new signal emitter
        self.set_port_button.clicked.connect(self._emit_com_port_setting)

        serial_settings_group.setLayout(serial_layout)
        layout.addWidget(serial_settings_group)
        # --- End New ---

        # Apply main layout
        self.setLayout(layout)

        # Optional size policy
        self.setMinimumWidth(180)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def update_coordinate(self, x, y, z):
        # Existing method for coordinate update
        self.x_label.setText(f"X: {x:.2f}")
        self.y_label.setText(f"Y: {y:.2f}")
        self.z_label.setText(f"Z: {z:.2f}")

    def _emit_com_port_setting(self):
        """Emits the text from the COM port input field."""
        port_name = self.port_input.text().strip()
        if port_name: # Only emit if not empty
            self.com_port_changed.emit(port_name)
            print(f"COM Port set to: {port_name}")
        else:
            print("COM Port field cannot be empty.")