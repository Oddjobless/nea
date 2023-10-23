import sys
import simulation
import time
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

[]
# Press the green button in the gutter to run the script.

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setBaseSize(QSize(200,200))
        self.button = QPushButton("Run sim")
        self.setCentralWidget(self.button)
        self.button.clicked.connect(self.buttonclick)

    def buttonclick(self):
        self.hide()
        simulation.run()
        self.show()
        print(":)")


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
