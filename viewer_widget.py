from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt


class ViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(500, 400)
        self.setStyleSheet("background-color: white;")

    def paintEvent(self, event):  
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        #fill background manually
        painter.fillRect(self.rect(), Qt.white)
        
        #draw canvas where the tracking will take place
        pen = QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(0,0,-1,-1))
        
        
        #draw crosshair just to test canvas
        center_x = self.width() // 2
        center_y = self.height() // 2
        painter.drawLine(center_x - 10, center_y, center_x + 10, center_y)
        painter.drawLine(center_x, center_y - 10, center_x, center_y + 10)
        #replace this with OpenGL or 3D rendering here ^ for tracking drone