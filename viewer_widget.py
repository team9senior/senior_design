from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PySide6.QtCore import Qt, QPointF
import math

class ViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(500, 400)
        self.setStyleSheet("background-color: lightgray;")
        self.current_angle_rad = 0.0 # Stores the angle calculated from arcsin

    def set_angle(self, angle_rad):
        """Sets the angle to be drawn and triggers a repaint."""
        self.current_angle_rad = angle_rad
        self.update() # Request a repaint of the widget

    def paintEvent(self, event):
        """Draws the polar graph, compass, and two ambiguous angle indicators."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fill background (canvas area)
        painter.fillRect(self.rect(), Qt.white)

        # Draw canvas border
        pen = QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

        # Center of the widget
        center_x = self.width() // 2
        center_y = self.height() // 2
        center = QPointF(center_x, center_y)

        # --- Polar Graph Elements ---
        compass_radius = min(self.width(), self.height()) / 3
        
        # Draw concentric circles (grid lines)
        painter.setPen(QPen(QColor(220, 220, 220), 1, Qt.DotLine)) # Light gray dotted lines
        num_circles = 3
        for i in range(1, num_circles + 1):
            radius = compass_radius * (i / num_circles)
            painter.drawEllipse(center, radius, radius)

        # Draw radial lines (grid lines)
        painter.setPen(QPen(QColor(220, 220, 220), 1, Qt.DotLine))
        num_radial_lines = 8 # Every 45 degrees
        for i in range(num_radial_lines):
            angle = i * (2 * math.pi / num_radial_lines)
            start_point = center
            end_x = center_x + compass_radius * math.cos(angle)
            end_y = center_y - compass_radius * math.sin(angle) # Y-axis inverted
            painter.drawLine(start_point, QPointF(end_x, end_y))

        # Draw main compass circle (solid line)
        painter.setPen(QPen(Qt.darkGray, 1))
        painter.drawEllipse(center, compass_radius, compass_radius)


        # --- Compass Labels ---
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        painter.setPen(Qt.black)

        # Labels for 0°, +90°, -90° (and 180° for ambiguity context)
        # Assuming 0° is "Ahead" (upwards on screen, which is -Y direction in screen coords)
        painter.drawText(int(center_x - 45), int(center_y - compass_radius - 15), "0° (Ahead)")
        painter.drawText(int(center_x + compass_radius + 5), int(center_y + 5), "+90° (Right)")
        painter.drawText(int(center_x - compass_radius - 45), int(center_y + 5), "-90° (Left)")
        
        # Add a "180° (Behind)" label for context of ambiguity
        painter.drawText(int(center_x - 50), int(center_y + compass_radius + 20), "180° (Behind)")


        # --- Draw Ambiguous Angle Indicators (Two Arrows) ---
        arrow_length = compass_radius * 0.8
        arrow_thickness = 4
        arrow_head_size = 15

        # First arrow: The directly calculated angle
        painter.setPen(QPen(Qt.red, arrow_thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QBrush(Qt.red))
        self._draw_arrow(painter, center, arrow_length, arrow_head_size, self.current_angle_rad)

        # Second arrow: The ambiguous angle (180 degrees rotated)
        # This angle represents the "behind" ambiguity.
        ambiguous_angle_rad = self.current_angle_rad + math.pi
        painter.setPen(QPen(Qt.blue, arrow_thickness, Qt.DotLine, Qt.RoundCap, Qt.RoundJoin)) # Dotted blue for ambiguous
        painter.setBrush(QBrush(Qt.blue))
        self._draw_arrow(painter, center, arrow_length, arrow_head_size, ambiguous_angle_rad)

        # --- Display the calculated angles in degrees ---
        angle_deg_primary = math.degrees(self.current_angle_rad)
        angle_deg_ambiguous = math.degrees(ambiguous_angle_rad)

        # Normalize ambiguous angle to be within 0-360 for consistent display
        angle_deg_primary_norm = (angle_deg_primary + 360) % 360
        angle_deg_ambiguous_norm = (angle_deg_ambiguous + 360) % 360
        
        # Sort them for consistent display
        display_angles = sorted([angle_deg_primary_norm, angle_deg_ambiguous_norm])


        painter.setPen(Qt.darkBlue)
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.drawText(
            int(center_x - 120), int(center_y + compass_radius + 40),
            f"Possible Angles: {display_angles[0]:.2f}° and {display_angles[1]:.2f}°"
        )
        # Indicate which one is "primary" (from arcsin) or "ambiguous"
        painter.setFont(QFont("Arial", 10))
        painter.drawText(
            int(center_x - 120), int(center_y + compass_radius + 60),
            f"(Primary: {angle_deg_primary:.2f}°, Ambiguous: {math.degrees(ambiguous_angle_rad):.2f}°)"
        )


    def _draw_arrow(self, painter, center, length, head_size, angle_rad):
        """Helper function to draw an arrow from the center at a given angle."""
        # Angle for drawing: 0 degrees is to the right, positive is counter-clockwise.
        # Our 0 degrees is "Up" (-Y in screen coords). Positive angle_rad is clockwise from Up.
        # So, the drawing angle is math.pi / 2 - angle_rad
        draw_angle_rad = math.pi / 2 - angle_rad

        tip_x = center.x() + length * math.cos(draw_angle_rad)
        tip_y = center.y() - length * math.sin(draw_angle_rad) # Y is inverted

        painter.drawLine(int(center.x()), int(center.y()), int(tip_x), int(tip_y))

        # Draw arrow head (two lines from the tip)
        head_angle_offset = math.radians(25) # Angle for arrowhead wings relative to the main arrow line

        p1_x = tip_x - head_size * math.cos(draw_angle_rad - head_angle_offset)
        p1_y = tip_y + head_size * math.sin(draw_angle_rad - head_angle_offset)

        p2_x = tip_x - head_size * math.cos(draw_angle_rad + head_angle_offset)
        p2_y = tip_y + head_size * math.sin(draw_angle_rad + head_angle_offset)

        painter.drawLine(int(tip_x), int(tip_y), int(p1_x), int(p1_y))
        painter.drawLine(int(tip_x), int(tip_y), int(p2_x), int(p2_y))
        #replace this with OpenGL or 3D rendering here ^ for tracking drone