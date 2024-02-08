import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

# from matplotlib import pyplot
from time import sleep


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ARGHHHHHHHHHH")
        self.setGeometry(100, 100, 600, 900)

        self.layout = QStackedLayout()
        self.index = QWidget()
        self.index.setLayout(self.layout)
        self.setCentralWidget(self.index)
        self.toolbar = QToolBar("ahshsh")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        self.setFont(QFont("Helvetica", 15))
        self.index.setStyleSheet("""
            {
                font-size: 40;
                font_family: 'Helvetica';
            }

            .plaintext {
                font-size:100
            }
        """)  # FIX

        ##################################################
        self.home_page_button = QAction("Home Page")
        self.toolbar.addAction(self.home_page_button)
        self.home_page_button.triggered.connect(lambda: self.changeIndex(0))
        self.home_page = QPushButton("Home page")
        self.home_page.setFont(QFont("Gadzoox", 30))
        self.layout.addWidget(self.home_page)
        self.toolbar.addSeparator()
        self.home_page.setStyleSheet("background-color: '#F49097';")

        ##################################################

        self.cipher1_button = QAction("Caesar Cipher", self)
        self.toolbar.addAction(self.cipher1_button)
        self.cipher1_button.triggered.connect(lambda: self.changeIndex(1))

        self.caesarCipher_layout = QGridLayout()
        self.caesarCipher = QWidget()
        self.caesarCipher.setStyleSheet("""
            QLineEdit {
                margin: 60;
                border: 3px solid '#0000ff';
            }

            QTextEdit {
                border: 2px dashed '#0000ff';
                margin: 30;
            }

            QPushButton {
                font-family: 'Comic Sans MS';
                font-size: 30px;
                padding: 20px 32px;
                color: green;
                border-radius: 6%;
                display: inline-block;
                position: fixed;
                margin: 0 0 0 0;
                transition-duration: 0.4s;
                border: 3px solid;
            }

            QPushButton:hover {
                background-color: '#0000ff';
                color: white;
            }

        """)
        self.caesarCipher_spaces = False

        self.caesarCipher_inputText = QTextEdit()
        self.caesarCipher_inputText.setFont(QFont("Helvetica", 16))
        self.caesarCipher_inputText.setObjectName("plaintext")
        self.caesarCipher_inputText.setPlaceholderText("Enter your text here (Leave blank to use default text)")

        self.caesarCipher_layout.addWidget(self.caesarCipher_inputText, 0, 0, 1, 1)

        self.caesarCipher_inputKey = QLineEdit()
        self.caesarCipher_inputKey.setPlaceholderText("Enter your key")
        self.caesarCipher_layout.addWidget(self.caesarCipher_inputKey, 0, 3, 1, 3)
        self.caesarCipher_inputKey.setFont(QFont("Inconsolata", 20))

        self.caesarCipher_encrypt = QPushButton("Encrypt")
        self.caesarCipher_layout.addWidget(self.caesarCipher_encrypt, 2, 3, 1, 1)
        self.caesarCipher_encrypt.setObjectName("encrypt")
        self.caesarCipher_encrypt.released.connect(lambda: self.caesar(True))

        self.caesarCipher_decrypt = QPushButton("Decrypt")
        self.caesarCipher_layout.addWidget(self.caesarCipher_decrypt, 2, 4)
        self.caesarCipher_decrypt.setObjectName("decrypt")
        self.caesarCipher_decrypt.released.connect(lambda: self.caesar(False))

        self.caesarCipher_output = QTextEdit()
        self.caesarCipher_output.setFont(QFont("Helvetica", 16))
        self.caesarCipher_output.setReadOnly(True)

        self.caesarCipher_layout.addWidget(self.caesarCipher_output, 1, 0, 1, 1)

        self.caesarCipher.setLayout(self.caesarCipher_layout)

        self.layout.addWidget(self.caesarCipher)

        # self.caesarCipher.setStyleSheet("background-color: '#DFB2F4';")
        ##################################################

        self.cipher2_button = QAction("Transposition Cipher", self)
        self.toolbar.addAction(self.cipher2_button)
        self.cipher2_button.triggered.connect(lambda: self.changeIndex(2))

        self.transpositionCipher_layout = QGridLayout()
        self.transpositionCipher = QWidget()
        self.transpositionCipher.setStyleSheet("""
            QLineEdit {
                margin: 60;
                border: 3px solid '#00ff00';
            }

            QTextEdit {
                border: 2px dashed '#00ff00';
                margin: 30;
            }

            QPushButton {
                font-family: 'Comic Sans MS';
                font-size: 30px;
                padding: 20px 32px;
                color: green;
                border-radius: 6%;
                display: inline-block;
                position: fixed;
                margin: 0 0 0 0;
                transition-duration: 0.4s;
                border: 3px solid;
            }

            QPushButton:hover {
                background-color: '#4caf50';
                color: white;
            }

        """)

        self.transpositionCipher_inputText = QTextEdit()
        self.transpositionCipher_inputText.setFont(QFont("Helvetica", 16))
        self.transpositionCipher_inputText.setObjectName("plaintext")
        self.transpositionCipher_inputText.setPlaceholderText("Enter your text here (Leave blank to use default text)")

        self.transpositionCipher_layout.addWidget(self.transpositionCipher_inputText, 0, 0, 1, 1)

        self.transpositionCipher_inputKey = QLineEdit()
        self.transpositionCipher_inputKey.setPlaceholderText("Enter your key")
        self.transpositionCipher_layout.addWidget(self.transpositionCipher_inputKey, 0, 3, 1, 3)
        self.transpositionCipher_inputKey.setFont(QFont("Inconsolata", 20))
        self.transpositionCipher_encrypt = QPushButton("Encrypt")
        self.transpositionCipher_layout.addWidget(self.transpositionCipher_encrypt, 2, 3, 1, 1)
        # self.transpositionCipher_encrypt.setObjectName("encrypt")
        self.transpositionCipher_encrypt.released.connect(lambda: self.transposition(True))

        self.transpositionCipher_decrypt = QPushButton("Decrypt")
        self.transpositionCipher_layout.addWidget(self.transpositionCipher_decrypt, 2, 4)
        # self.transpositionCipher_decrypt.setObjectName("decrypt")
        self.transpositionCipher_decrypt.clicked.connect(lambda: self.transposition(False))

        self.transpositionCipher_output = QTextEdit()
        self.transpositionCipher_output.setFont(QFont("Helvetica", 16))
        self.transpositionCipher_output.setReadOnly(True)

        self.transpositionCipher_layout.addWidget(self.transpositionCipher_output, 1, 0, 1, 1)

        self.transpositionCipher.setLayout(self.transpositionCipher_layout)

        self.layout.addWidget(self.transpositionCipher)

        ##################################################

        self.cipher3_button = QAction("One Time Pad", self)
        self.toolbar.addAction(self.cipher3_button)
        self.cipher3_button.triggered.connect(lambda: self.changeIndex(3))

        self.oneTimeCipher_layout = QGridLayout()
        self.oneTimeCipher = QWidget()
        self.oneTimeCipher.setStyleSheet("""
            QLineEdit {
                margin: 60;
                border: 3px solid '#ff0000';
            }

            QTextEdit {
                border: 2px dashed '#ff0000';
                margin: 30;
            }

            QPushButton {
                font-family: 'Comic Sans MS';
                font-size: 30px;
                padding: 20px 32px;
                color: green;
                border-radius: 6%;
                display: inline-block;
                position: fixed;
                margin: 0 0 0 0;
                transition-duration: 0.4s;
                border: 3px solid;
            }

            QPushButton:hover {
                background-color: '#ff0000';
                color: white;
            }

        """)

        self.oneTimeCipher_inputText = QTextEdit()
        self.oneTimeCipher_inputText.setFont(QFont("Helvetica", 16))
        self.oneTimeCipher_inputText.setObjectName("plaintext")
        self.oneTimeCipher_inputText.setPlaceholderText("Enter your text here (Leave blank to use default text)")

        self.oneTimeCipher_spaces = False

        self.oneTimeCipher_layout.addWidget(self.oneTimeCipher_inputText, 0, 0, 1, 1)

        self.oneTimeCipher_inputKey = QLineEdit()
        self.oneTimeCipher_inputKey.setPlaceholderText("Enter your key")
        self.oneTimeCipher_layout.addWidget(self.oneTimeCipher_inputKey, 0, 3, 1, 3)

        self.oneTimeCipher_outputKey = QTextEdit()
        self.oneTimeCipher_outputKey.setReadOnly(True)
        self.oneTimeCipher_outputKey.setPlaceholderText("KEY")
        self.oneTimeCipher_layout.addWidget(self.oneTimeCipher_outputKey, 1, 3, 1, 2)

        self.oneTimeCipher_encrypt = QPushButton("Encrypt")
        self.oneTimeCipher_layout.addWidget(self.oneTimeCipher_encrypt, 2, 3, 1, 1)
        self.oneTimeCipher_encrypt.released.connect(lambda: self.oneTime(True))

        self.oneTimeCipher_decrypt = QPushButton("Decrypt")
        self.oneTimeCipher_layout.addWidget(self.oneTimeCipher_decrypt, 2, 4)
        self.oneTimeCipher_decrypt.clicked.connect(lambda: self.oneTime(False))

        self.oneTimeCipher_output = QTextEdit()
        self.oneTimeCipher_output.setFont(QFont("Helvetica", 16))
        self.oneTimeCipher_output.setReadOnly(True)
        self.oneTimeCipher_layout.addWidget(self.oneTimeCipher_output, 1, 0, 1, 1)

        self.oneTimeCipher.setLayout(self.oneTimeCipher_layout)

        self.layout.addWidget(self.oneTimeCipher)


        ##################################################
        self.toolbar.addSeparator()

        self.cipher4_button = QAction("Square Multiply", self)
        self.toolbar.addAction(self.cipher4_button)
        self.cipher4_button.triggered.connect(lambda: self.changeIndex(4))

        self.squareMultiply_layout = QStackedLayout()
        self.squareMultiply = QWidget()
        self.squareMultiply.setLayout(self.squareMultiply_layout)

        self.ss1 = QLabel()
        self.ss1.setPixmap(QPixmap("ss1.png"))
        self.ss2 = QLabel()
        self.ss2.setPixmap(QPixmap("ss2.png"))
        self.ss3 = QLabel()
        self.ss3.setPixmap(QPixmap("ss3.png"))
        self.ss4 = QLabel()
        self.ss4.setPixmap(QPixmap("ss4.png"))
        self.ss5 = QLabel()
        self.ss5.setPixmap(QPixmap("ss5.png"))
        self.ss6 = QLabel()
        self.ss6.setPixmap(QPixmap("ss6.png"))
        self.ss7 = QLabel()
        self.ss7.setPixmap(QPixmap("ss7.png"))
        self.ss8 = QLabel()
        self.ss8.setPixmap(QPixmap("ss8.png"))
        self.ss9 = QLabel()
        self.ss9.setPixmap(QPixmap("ss9.png"))

        #self.squareMultiply.mousePressEvent(self.squareMultiply_ppt)
        self.slides = [self.ss1,self.ss2,self.ss3,self.ss4,self.ss5,self.ss6,self.ss7,self.ss8,self.ss9]
        for i in self.slides:
            self.squareMultiply_layout.addWidget(i)
            i.setBaseSize(QSize(1280,720))

            i.setScaledContents(True)

        self.squareMultiply.setStyleSheet("""
        QPixmap {
            height: auto;
            width: 100%;    
        }
        """)



        self.layout.addWidget(self.squareMultiply)


        ##################################################
        self.setStyleSheet("""
            {
            }
        """)

    def changeIndex(self, newIndex):  # FIX THIS
        self.layout.setCurrentIndex(newIndex)

    def caesar(self, arghhhh):
        self.caesarCipher_output.setText(
            (ciphers.caesarCipher((self.caesarCipher_inputText.toPlainText()), self.caesarCipher_inputKey.text(),
                                  encrypt=arghhhh, spaces=self.caesarCipher_spaces)))

    def transposition(self, s):
        self.transpositionCipher_output.setText((ciphers.transposition(
            (self.transpositionCipher_inputText.toPlainText()), self.transpositionCipher_inputKey.text(), encrypt=s)))

    def oneTime(self, s):
        output, key = (ciphers.oneTimePad((self.oneTimeCipher_inputText.toPlainText()),
                                                              self.oneTimeCipher_inputKey.text(), encrypt=s,
                                                              spaces=self.oneTimeCipher_spaces))

        print(output, key)
        self.oneTimeCipher_output.setText(output)
        self.oneTimeCipher_outputKey.setText(key)

    def keyPressEvent(self, event):
        if event.key() == 16777217:
            self.squareMultiply_layout.setCurrentIndex((self.squareMultiply_layout.currentIndex() + 1) % len(self.slides))

    def nextSlide(self):
        print()



app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())

##55D6C2, #64DAC8

from random import randrange

'''
PLAN:
make ciphers
put into pyqt
 freequency analysis
context menu for optional stuff

from PyQt6 # cant install it


# square multiply

generator = 3 #######
public1 = 235~

'''
