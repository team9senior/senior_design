# app.py (main launcher)
import sys
import time
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    # Splash screen
    splash_pixmap = QPixmap("splashpage.jpg")
    splash_screen = QSplashScreen(splash_pixmap)
    splash_screen.setMask(splash_pixmap.mask())
    splash_screen.show()
    time.sleep(1)

    # Main Window
    window = MainWindow()
    splash_screen.finish(window)
    window.show()

    app.exec()

if __name__ == "__main__":
    main()
