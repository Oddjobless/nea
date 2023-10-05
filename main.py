import sys
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setBaseSize(QSize(200,200))

        self.setCentralWidget(QPushButton("ADFSdsfsdsgd"))

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()