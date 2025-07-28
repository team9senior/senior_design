# app.py (main launcher)
import sys
import os 
import time
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from main_window import MainWindow

# --- Add this helper function ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If not running in PyInstaller, use the current directory
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# --- End of helper function ---


def main():
    app = QApplication(sys.argv)

    # Splash screen
    # Use the resource_path function to correctly locate the image
    splash_pixmap = QPixmap(resource_path("splashpage.jpg"))
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