import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from Simulations import simulation, ProjectileMoitionSimulation, test, coolParticleStuff, fluidFlowSimulation
from database import Database
from hashlib import sha256

# from matplotlib import pyplot


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.database = Database("localhost", "root", "2121", "NEA")


        self.setWindowTitle("ARGHHHHHHHHHH")
        self.setGeometry(0, 0, 1920, 1080)
        self.showFullScreen() # todo: fullscreen
        self.layout = QStackedLayout()
        self.index = QWidget()
        self.index.setLayout(self.layout)
        self.setCentralWidget(self.index)
        self.toolbar = QToolBar("ahshsh")
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(False)

        self.setFont(QFont("Helvetica", 15))
        self.index.setStyleSheet("""
            {
                font-size: 60;
                font_family: 'Helvetica';
            }

            .plaintext {
                font-size:100
            }
        """)  # FIX

        #################################################

        self.login_layout = QGridLayout()
        self.login = QWidget()
        self.login.setLayout(self.login_layout)

        self.login_label = QLabel("Login")
        self.login_layout.addWidget(self.login_label, 0, 1, 1, 1)


        self.email = QLineEdit()
        self.email.setPlaceholderText("Enter email address")
        self.login_layout.addWidget(self.email, 7, 0, 1, 7)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_layout.addWidget(self.password, 8, 0, 1, 4)


        self.login_button = QPushButton("Attempt Login")
        self.login_button.released.connect(self.attempt_login)
        self.login_layout.addWidget(self.login_button,9, 4, 1, 1)



        self.toggle_login = QPushButton("Already Have\nAn Account?")
        self.toggle_login.released.connect(self.toggle_login_register)
        self.login_layout.addWidget(self.toggle_login, 9, 1, 1, 1)


        # registration widgets
        self.repeat_password = QLineEdit()
        self.repeat_password.setPlaceholderText("Enter Your Password Again")
        self.repeat_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_layout.addWidget(self.repeat_password, 8, 0, 1, 4)
        self.repeat_password.hide()

        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Enter your full name")
        self.login_layout.addWidget(self.full_name, 4, 0, 1, 4)
        self.full_name.hide()

        self.date_of_birth = QDateEdit()
        self.date_of_birth.setDisplayFormat("dd/MM/yyyy")
        self.date_of_birth.setCalendarPopup(True)
        self.login_layout.addWidget(self.date_of_birth, 6, 1, 1, 2)
        self.date_of_birth.hide()
        self.date_of_birth_label = QLabel("Date of\n Birth")
        self.login_layout.addWidget(self.date_of_birth_label, 6, 0, 1, 1)
        self.date_of_birth_label.hide()



        self.layout.addWidget(self.login)
        self.login.setStyleSheet("""

            QLabel {
                font-family: 'Comic Sans MS';
                font-size: 30px;
                align: right;
                margin-left: 30px;
            }
            QLineEdit {
                margin: 20px 50px 0px 30px;;
                border: 10px solid '#0000ff';
                font-size: 30px;
                padding: 10px;
            }

            QTextEdit {
                border: 2px dashed '#0000ff';
                margin: 60px;
            }

            QPushButton, QDateEdit {
                font-family: 'Comic Sans MS';
                font-size: 40px;
                padding: 10px 20px;
                color: green;
                border-radius: 10%;
                display: inline-block;
                position: fixed;
                margin: 30px 30px 30px 0px;
                transition-duration: 0.9s;
                border: 2px solid;
                align: right;
            }

            QPushButton:hover {
                background-color: '#0000ff';
                color: white;
            }
        """)

        ##################################################
        self.home_page_button = QAction("Home Page")
        self.toolbar.addAction(self.home_page_button)
        self.home_page_button.triggered.connect(lambda: self.changeIndex(1))
        self.home_page = QPushButton("Home page")
        self.home_page.setFont(QFont("Gadzoox", 30))
        self.layout.addWidget(self.home_page)
        self.toolbar.addSeparator()
        self.home_page.setStyleSheet("background-color: '#F49097';")


        ##################################################

        self.cipher1_button = QAction("Caesar Cipher", self)
        self.toolbar.addAction(self.cipher1_button)
        self.cipher1_button.triggered.connect(lambda: self.changeIndex(2))

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

        self.caesarCipher_encrypt.released.connect(self.caesar)

        self.caesarCipher_decrypt = QPushButton("Decrypt")
        self.caesarCipher_layout.addWidget(self.caesarCipher_decrypt, 2, 4)
        self.caesarCipher_decrypt.setObjectName("decrypt")

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
        self.cipher2_button.triggered.connect(lambda: self.changeIndex(3))

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
        self.transpositionCipher_encrypt.released.connect(self.transposition)

        self.transpositionCipher_decrypt = QPushButton("Decrypt")
        self.transpositionCipher_layout.addWidget(self.transpositionCipher_decrypt, 2, 4)
        # self.transpositionCipher_decrypt.setObjectName("decrypt")


        self.transpositionCipher_output = QTextEdit()
        self.transpositionCipher_output.setFont(QFont("Helvetica", 16))
        self.transpositionCipher_output.setReadOnly(True)

        self.transpositionCipher_layout.addWidget(self.transpositionCipher_output, 1, 0, 1, 1)
        self.transpositionCipher.setLayout(self.transpositionCipher_layout)

        self.layout.addWidget(self.transpositionCipher)

        ##################################################

        self.cipher3_button = QAction("One Time Pad", self)
        self.toolbar.addAction(self.cipher3_button)
        self.cipher3_button.triggered.connect(lambda: self.changeIndex(4))

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

        self.Test_Sim = QPushButton("Test")
        self.Test_Sim.released.connect(self.oneTime)
        self.oneTimeCipher_layout.addWidget(self.Test_Sim, 0, 1, 1, 1)





        self.oneTimeCipher.setLayout(self.oneTimeCipher_layout)

        self.layout.addWidget(self.oneTimeCipher)


        ##################################################
        self.toolbar.addSeparator()

        self.cipher4_button = QAction("Square Multiply", self)
        self.toolbar.addAction(self.cipher4_button)
        self.cipher4_button.triggered.connect(lambda: self.changeIndex(5))

        self.squareMultiply_layout = QGridLayout()
        self.squareMultiply = QWidget()
        self.squareMultiply.setLayout(self.squareMultiply_layout)
        self.layout.addWidget(self.squareMultiply)

        self.runCool = QPushButton("Run ideal gas simulation")
        self.squareMultiply_layout.addWidget(self.runCool, 0, 0, 1, 1)
        self.runCool.released.connect(self.particleSim)


        self.runPoo = QPushButton("DO NOT CLICK THIS. DO NOT CLICK THIS. DO NOT CLICK THIS. DO NOT CLICK THIS. DO NOT CLICK THIS.")
        self.squareMultiply_layout.addWidget(self.runPoo, 1, 1, 1,3)
        self.runPoo.released.connect(self.brokenSim)



        ##################################################
        self.setStyleSheet("""
            {
            }
        """)

    def changeIndex(self, newIndex):  # FIX THIS
        self.layout.setCurrentIndex(newIndex)


    def attempt_login(self):
        user_info = self.database.verify_login(self.email.text(), sha256(self.password.text().encode()).hexdigest())
        if user_info:
            self.user_info = user_info
            self.show_toolbar()
            # todo: display success message
        else:
            print("Fail") # todo:

    def toggle_login_register(self):
        if self.toggle_login.text()[0] == "A":
            self.toggle_login.setText("Don't have\n an account?")
            self.full_name.hide()
            self.date_of_birth.hide()
            self.date_of_birth_label.hide()
            self.repeat_password.hide()

            self.login_layout.removeWidget(self.password)
            self.login_layout.removeWidget(self.email)
            self.login_layout.addWidget(self.email, 5, 0, 1, 4)
            self.login_layout.addWidget(self.password, 6, 0, 1, 4)


        else:
            self.toggle_login.setText("Already have\n an account?")

            self.full_name.show()
            self.date_of_birth.show()
            self.date_of_birth_label.show()
            self.repeat_password.show()


            self.login_layout.removeWidget(self.password)
            self.login_layout.removeWidget(self.email)
            self.login_layout.addWidget(self.email, 8, 0, 1, 4)
            self.login_layout.addWidget(self.password, 7, 0, 1, 4)


    def switch_to_login(self):
        if self.toggle_login.text()[0] == "A":
            self.login_layout.addWidget()

        else:
            pass
            # self.login_layout.removeWidget() todo: remove widgets from registering




    def show_toolbar(self):
        self.toolbar.setVisible(True)

    def hide_toolbar(self):
        self.toolbar.setVisible(False)

    def caesar(self):
        ProjectileMoitionSimulation.run()

    def transposition(self):
        simulation.run()


    def oneTime(self):
        test.run()

    def particleSim(self):
        coolParticleStuff.run()

    def brokenSim(self):
        fluidFlowSimulation.run()


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
