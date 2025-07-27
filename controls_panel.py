from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QSlider, QGroupBox,
    QHBoxLayout, QSizePolicy
)
from PySide6.QtCore import Qt

#update this for real time tracking at main app.py - july 26
class ControlsPanel(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Heading
        header = QLabel("Controls")
        header.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(header)
        
        # Coordinates Group
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

        # Update Button
        self.update_button = QPushButton("Update")
        layout.addWidget(self.update_button)

        # Apply layout
        self.setLayout(layout)

        # Optional size
        self.setMinimumWidth(180)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def update_coordinate(self, x: float, y: float, z: float):
    ## This needs to be integrated to the mcu for update pinning from TDOA
        self.x_label.setText(f"X: {x:.2f}")
        self.y_label.setText(f"Y: {y:.2f}")
        self.z_label.setText(f"Z: {z:.2f}")