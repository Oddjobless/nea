import sys
import traceback
# add weekly score to database
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from Simulations import pathfinderSimulation, projectileMotionSimulation, test, idealGasLawSimulation, fluidFlowSimulation
from database import Database
from hashlib import sha256
import re

# from matplotlib import pyplot

 #
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.database = Database("localhost", "root", "2121", "NEA")

        self.user_settings = [None, None, 18, 32, 0.8, 500, 1]
        self.setWindowTitle("ARGHHHHHHHHHH")
        self.setGeometry(0, 0, 1920, 1080)
        self.showFullScreen()  # todo: fullscreen

        self.layout = QStackedLayout()

        self.index = QWidget()
        self.index.setLayout(self.layout)
        self.setCentralWidget(self.index)
        self.toolbar = QToolBar("ahshsh")
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(False)
        self.toolbar.hide()


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
        """login_pixmap = QPixmap("./Simulations/SimulationFiles/Assets/images/login_background.jpg")
        login_background = QLabel()
        login_background.setPixmap(login_pixmap)
        login_background.setGeometry(0, 0, self.login.width(), self.login.height())
        login_background.setScaledContents(True)
        login_background.raise_()
        login_background.setContentsMargins(0, 0, 0, 0)
        self.login_layout.addWidget(login_background, 0, 0, 11, 7)"""
        self.login.setAutoFillBackground(True)  #
        palette = self.login.palette()  #
        palette.setColor(self.login.backgroundRole(), QColor(255, 249, 196))
        self.login.setPalette(palette)


        self.login_label = QLabel("Physics Simulator") # todo:
        self.login_label.setStyleSheet("""
        font-family: 'Times New Roman';
        font-size: 100px;""")
        self.login_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_layout.addWidget(self.login_label, 0, 2, 1, 2)



        self.email = QLineEdit()
        self.email.setPlaceholderText("Enter email address")
        self.email.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_layout.addWidget(self.email, 7, 0, 1, 6)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_layout.addWidget(self.password, 8, 0, 1, 6)

        self.login_button = QPushButton("Log in")
        self.login_button.released.connect(self.login_or_register)
        self.login_button.setMaximumWidth(350)
        self.login_layout.addWidget(self.login_button, 9, 3, 1, 1)

        self.toggle_login = QPushButton("Don't Have\nAn Account?")
        self.toggle_login.setMaximumWidth(350)
        self.toggle_login.released.connect(self.toggle_login_register)
        self.login_layout.addWidget(self.toggle_login, 9, 2, 1, 1)

        # registration widgets

        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Enter your full name")
        self.full_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_layout.addWidget(self.full_name, 4, 1, 1, 4)
        self.full_name.hide()



        self.date_of_birth = QDateEdit()
        # self.date_of_birth.setStyleSheet("padding-right: 10px;")
        self.date_of_birth.setDisplayFormat("dd/MM/yyyy")
        # self.date_of_birth.setMaximumWidth(600)
        self.date_of_birth.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.date_of_birth.setCalendarPopup(True)
        self.login_layout.addWidget(self.date_of_birth, 6, 1, 1, 2)
        self.date_of_birth.hide()

        self.date_of_birth_label = QLabel("Date of Birth")
        self.login_layout.addWidget(self.date_of_birth_label, 6, 1, 1, 1)
        self.date_of_birth_label.hide()

        teachers = []
        for record in self.database.get_teacher_names():
            teachers.append(f"{record[0]}")
        self.teacher_dropdown = QComboBox()
        self.teacher_dropdown.addItems(teachers)

        self.login_layout.addWidget(self.teacher_dropdown, 6, 3, 1, 2)
        self.teacher_dropdown.hide()


        self.layout.addWidget(self.login)
        self.login.setStyleSheet("""

            QLabel {
                font-family: 'Comic Sans MS';
                font-size: 30px;
                align: right;
                margin-left: 30px;
            }
      
            
            QLineEdit {
                margin: 20px 200px 0px 200px;;
                border: 10px solid '#ffab40';
                font-size: 30px;
                padding: 10px;
                width: 600px;
            }
            
            QTextEdit {
                border: 2px dashed '#0000ff';
                margin: 60px;
            }

            QPushButton, QDateEdit, QComboBox {
                
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
            QPushButton {background-color: '#d7ffcc';font-family: 'Comic Sans MS';}
            QPushButton:hover {background-color: '#abff94';}
        """)

        ##################################################
        self.home_page_button = QAction("Home Page")
        self.toolbar.addAction(self.home_page_button)
        self.home_page_button.triggered.connect(lambda: self.changeIndex(1))
        self.home_page = QPushButton("Log Off")
        self.home_page.released.connect(self.log_off)
        self.home_page.setFont(QFont("Gadzoox", 30))
        self.layout.addWidget(self.home_page)
        self.toolbar.addSeparator()
        self.home_page.setStyleSheet("background-color: '#F49097';")

        ##################################################

        self.projectile_button = QAction("Projectile Motion", self)
        self.toolbar.addAction(self.projectile_button)
        self.projectile_button.triggered.connect(lambda: self.changeIndex(2))

        self.projectile_widget_layout = QGridLayout()
        self.projectile_widget = QWidget()

        self.projectile_widget.setAutoFillBackground(True)  #
        palette = self.projectile_widget.palette()  #
        palette.setColor(self.projectile_widget.backgroundRole(), QColor(232, 179, 220))
        self.projectile_widget.setPalette(palette)

        self.projectile_widget.setStyleSheet("""
            QLineEdit {
                margin: 60;
                border: 3px solid '#0000ff';
            }

            QTextEdit {
                border: 2px dashed '#0000ff';
                margin: 30;
            }
            
            QLabel{
                font-family: 'Comic Sans MS';
                font-size: 30px;
            }

            QPushButton, QSpinBox {
                font-family: 'Comic Sans MS';
                font-size: 30px;
                padding: 20px 32px;
                color: '#';
                border-radius: 6%;
                display: inline-block;
                position: fixed;
                margin: 0 0 0 0;
                transition-duration: 0.4s;
                border: 3px solid;
            }
            QPushButton {background-color: '#F9B5AC';}

            QPushButton:hover {
                background-color: '#ffb468';
                color: white;
            }

        """)
        self.projectile_widget.setLayout(self.projectile_widget_layout)

        self.projectile_sim_buttons = [QPushButton("Level\n" + str(x + 1)) for x in range(9)]
        for index, button in enumerate(self.projectile_sim_buttons):
            button.setCheckable(False)
            button.setCursor(QCursor(Qt.CursorShape.ForbiddenCursor))
            self.projectile_widget_layout.addWidget(button, self.projectile_sim_buttons.index(button) // 3,
                                                    (2 * ((self.projectile_sim_buttons.index(button)) % 3) + 3), 1, 1)
            button.setMaximumWidth(300)
            button.setMinimumHeight(150)
        self.weeklyButton = QPushButton("Level of\nthe Week")
        self.weeklyButton.setMaximumWidth(400)
        self.enable_projectile_button(self.weeklyButton)
        self.weeklyButton.released.connect(lambda: self.run_projectile_motion_sim("Weekly"))
        self.weeklyScore = 0

        self.air_resistance_button = QPushButton("Air Resistance\nENABLED")
        self.toggle_air_resistance_button()
        self.air_resistance_button.setMaximumWidth(240)
        self.air_resistance_button.released.connect(self.toggle_air_resistance_button)
        self.air_resistance_button.setCheckable(True)
        self.projectile_widget_layout.addWidget(self.air_resistance_button, 2, 0, 1, 1)

        

        self.projectile_instruction = QLabel()
        self.projectile_instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.projectile_instruction.setWordWrap(True)
        self.projectile_instruction.setText("""Welcome to the
Projectile Motion Simulation!   
The aim of the game is to fire the ball into the target. 
The closer to the centre you are, the more score! 
Use suvat equations to calculate the required velocity.    
Get 100 score to unlock the next level. 
    
Controls:   
LMB to move the ball    
RMB to project the ball 
t: show parameters table    
v: toggle velocity view 
q: quit""")
        self.projectile_widget_layout.addWidget(self.projectile_instruction, 0, 0, 2, 3)

        self.layout.addWidget(self.projectile_widget)
        ##################################################

        self.pathfinding_button = QAction("Vector Field Pathfinding", self)
        self.toolbar.addAction(self.pathfinding_button)
        self.pathfinding_button.triggered.connect(lambda: self.changeIndex(3))

        self.pathfinding_layout = QGridLayout()
        self.pathfinding = QWidget()

        self.pathfinding.setAutoFillBackground(True)  #
        palette = self.pathfinding.palette()  #
        palette.setColor(self.pathfinding.backgroundRole(), QColor(209, 245, 255))
        self.pathfinding.setPalette(palette)

        self.pathfinding.setStyleSheet("""
            QLineEdit {
                margin: 60;
                border: 3px solid '#00ff00';
            }

            QTextEdit {
                border: 2px dashed '#00ff00';
                margin: 30;
            }
            

            QPushButton, QSpinBox, QLabel, QSlider{
                background-color: '#aff8f0';
                font-family: 'Comic Sans MS';
                font-size: 30px;
                padding: 20px;
                color: '#540d6e';
                border-radius: 6%;
                display: inline-block;
                position: fixed;
                margin: 0 0 0 0;
                transition: 0.4s;
                border: 3px solid;
            }

            QPushButton:hover {
                background-color: '#83f28f';
                color: white;
            }
            
            QSlider {
                
            }
            

        """)

        self.pathfinding_rows = QSpinBox() # no of rows in simulation
        self.pathfinding_rows.setRange(4, 100)
        self.pathfinding_layout.addWidget(self.pathfinding_rows, 0, 0, 1, 1)
        self.pathfinding_rows.setValue(self.user_settings[2]) # adding saved initial value

        self.pathfinding_cols = QSpinBox() # no of cols
        self.pathfinding_cols.setRange(4, 100)
        self.pathfinding_layout.addWidget(self.pathfinding_cols, 0, 2, 1, 1)
        self.pathfinding_cols.setValue(self.user_settings[3])

        self.pathfinding_speed = QSlider()  # desired velocity magnitude for steering behaviour
        self.pathfinding_speed.setOrientation(Qt.Orientation.Horizontal)
        self.pathfinding_speed.setRange(1, 100)
        self.pathfinding_speed.setValue(self.user_settings[5]) # adding saved initial value
        self.pathfinding_speed.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.pathfinding_layout.addWidget(self.pathfinding_speed, 2, 1, 1, 3)

        self.pathfinding_speed_label = QLabel(f"Particle speed = {self.pathfinding_speed.value()}")
        self.pathfinding_speed.valueChanged.connect(lambda: self.pathfinding_speed_label.setText(f"Particle speed = {self.pathfinding_speed.value()}"))
        self.pathfinding_layout.addWidget(self.pathfinding_speed_label, 2, 0, 1, 1)



        self.pathfinding_run = QPushButton("Run")
        self.pathfinding_layout.addWidget(self.pathfinding_run, 5, 2, 1, 1)
        self.pathfinding_run.released.connect(self.run_pathfinder)



        # self.noOfRows = Q

        self.pathfinding.setLayout(self.pathfinding_layout)
        self.layout.addWidget(self.pathfinding)

        ##################################################

        self.suspension_button = QAction("One Time Pad", self)
        self.toolbar.addAction(self.suspension_button)
        self.suspension_button.triggered.connect(lambda: self.changeIndex(4))

        self.suspension_layout = QGridLayout()
        self.suspension = QWidget()
        self.suspension.setStyleSheet("""

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
                background-color: '#83f28f';
                color: white;
            }

        """)

        self.Test_Sim = QPushButton("Test")
        self.Test_Sim.released.connect(self.run_suspension_sim)
        self.suspension_layout.addWidget(self.Test_Sim, 0, 1, 1, 1)

        self.suspension.setLayout(self.suspension_layout)

        self.layout.addWidget(self.suspension)

        ##################################################
        self.toolbar.addSeparator()

        self.ideal_gas_button = QAction("Ideal Gas Simulation", self)
        self.toolbar.addAction(self.ideal_gas_button)
        self.ideal_gas_button.triggered.connect(lambda: self.changeIndex(5))

        self.ideal_gas_layout = QGridLayout()
        self.ideal_gas = QWidget()
        self.ideal_gas.setLayout(self.ideal_gas_layout)
        self.layout.addWidget(self.ideal_gas)

        self.ideal_gas.setAutoFillBackground(True)  #
        palette = self.ideal_gas.palette()  #
        palette.setColor(self.ideal_gas.backgroundRole(), QColor(200, 249, 202))
        self.ideal_gas.setPalette(palette)

        self.ideal_gas.setStyleSheet("""
                    QLineEdit {
                        margin: 60;
                        border: 3px solid '#00ff00';
                    }

                    QTextEdit {
                        border: 2px dashed '#00ff00';
                        margin: 30;
                    }


                    QPushButton {
                        background-color: '#7AF0B7';
                        font-family: 'Comic Sans MS';
                        font-size: 30px;
                        padding: 20px;
                        color: '#6B5E62';
                        border-radius: 6%;
                        display: inline-block;
                        position: fixed;
                        margin: 0 0 0 0;
                        transition: 0.4s;
                        border: 3px solid;
                    }

                    QPushButton:hover {
                        background-color: '#83f28f';
                        color: white;
                    }""")

        self.runCool = QPushButton("Run ideal gas simulation")
        self.ideal_gas_layout.addWidget(self.runCool, 0, 0, 1, 1)
        self.runCool.released.connect(self.particleSim)

        self.runPoo = QPushButton(
            "DO NOT CLICK THIS. DO NOT CLICK THIS. DO NOT CLICK THIS. DO NOT CLICK THIS. DO NOT CLICK THIS.")
        self.ideal_gas_layout.addWidget(self.runPoo, 1, 1, 1, 3)
        self.runPoo.released.connect(self.brokenSim)

        ##################################################
        self.setStyleSheet("""
            {
            QPushButton {
                cursor: pointer;
            }

        """)

    def changeIndex(self, newIndex):  # FIX THIS
        self.layout.setCurrentIndex(newIndex)

    def attempt_login(self):
        email, password = self.email.text().strip(), sha256(self.password.text().encode()).hexdigest()
        user_info = self.database.verify_login(email, password)
        if user_info:
            self.user_info = user_info
            self.user_settings = self.database.get_user_settings(self.user_info[0])

            if not user_info[-1]: #if user isnt a teacher:
                self.teacher_id = self.database.get_teacher_id_by_user_id(self.user_info[0])
            else:
                self.teacher_id = None


            self.initialise_program(self.user_settings)
            self.show_toolbar()
            self.changeIndex(1)

            print("Logged in successfully")
            return True
        else:
            print(email, password)
            QMessageBox.critical(self, "Verification Failed", "Invalid email or password")
            return False

    def login_or_register(self):
        if self.toggle_login.text()[0] == "A":
            self.create_new_db_user()
        else:
            try:
                self.attempt_login()
            except Exception as e:
                print(e)

    def create_new_db_user(self):
        valid = True
        detailed_text = ""
        try:
            if len(self.password.text()) < 6:
                detailed_text += "Password must be at least 6 characters.\n"
                valid = False
            if self.email.text() == "":
                detailed_text += "No email given.\n"
                valid = False

            elif not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", self.email.text()):
                detailed_text += "Email is not valid.\n"
                valid = False

            if len(self.email.text()) > 256:
                detailed_text += "Email is too long.\n"
                valid = False

            if self.full_name.text() == "":
                detailed_text += "Full name is not given.\n"
                valid = False
            if self.date_of_birth.date().addYears(16) > QDate.currentDate():
                detailed_text += "You must be at least 16 years old.\n"
                valid = False

            assert valid # send to database to create user
            teacher = self.database.get_teacher_email_by_name(self.teacher_dropdown.currentText())
            user_created = self.database.create_user(self.email.text(), sha256(self.password.text().encode()).hexdigest(),
                                      self.full_name.text(), self.date_of_birth.date().toString("yyyy-MM-dd"), teacher_email=teacher)
            if not user_created:
                raise AssertionError
            self.toggle_login_register() # prompt user to login
            return True
        except AssertionError:
            box = QMessageBox()
            box.setText("Could not create a new account\nPlease check you have entered your information correctly.")
            box.setDetailedText(detailed_text)
            box.setIcon(QMessageBox.Icon.Warning)
            box.setWindowTitle("Registration Failed")
            box.exec()

            return False

    def toggle_login_register(self):
        if self.toggle_login.text()[0] == "A":
            self.toggle_login.setText("Don't have\n an account?")
            self.login_button.setText("Log in")
            self.full_name.hide()
            self.date_of_birth.hide()
            self.date_of_birth_label.hide()
            self.date_of_birth_label.hide()
            self.teacher_dropdown.hide()

        else:
            self.toggle_login.setText("Already have\n an account?")
            self.login_button.setText("Register")
            self.full_name.show()
            self.date_of_birth.show()
            self.date_of_birth_label.show()
            self.teacher_dropdown.show()
    def show_toolbar(self):
        self.toolbar.setVisible(True)

    def hide_toolbar(self):
        self.toolbar.setVisible(False)
    
    def toggle_air_resistance_button(self):
        text = self.air_resistance_button.text()
        if "DISABLED" in text:
            self.air_resistance_button.setText("Air Resistance\nENABLED")
            self.air_resistance_button.setStyleSheet("""
            QPushButton {
            font-family: 'Times New Roman';
            background-color: rgba(0, 255, 0, 0.3);
            color: black;
            } """)
        else:
            self.air_resistance_button.setText("Air Resistance\nDISABLED")
            self.air_resistance_button.setStyleSheet("""
            QPushButton {
            font-family: 'Times New Roman';
            background-color: rgba(255, 0, 0, 0.3);
            color: black;
            } """)


    def run_projectile_motion_sim(self, level_no):
        print(level_no)
        try:
            print(self.air_resistance_button.isChecked())
            if self.teacher_id is None:
                projectileMotionSimulation.draw_mode(level_no, self.penetration_factor_button.value()/100)

            score = projectileMotionSimulation.run(level_no, self.air_resistance_button.isChecked())
            if score:
                if score > 100 and level_no != "Weekly":
                    print("Winner!")
                    print(level_no)
                    button = self.projectile_sim_buttons[level_no]
                    self.enable_projectile_button(button, level_no)
                else: 
                    if score > self.weeklyScore:
                        self.weeklyScore = score
                        self.weeklyButton.setText(f"Level of the Week\nCurrent Score: {self.weeklyScore}")
        except Exception as e:
            pass
            # traceback.print_exc()


    def run_pathfinder(self):
        try:
            row = self.pathfinding_rows.value()
            col = self.pathfinding_cols.value()
            if row / col != self.height() / self.width(): # if rectangular cells
                print(row/col, self.height() / self.width())
                warning_box = QMessageBox()
                warning_box.setWindowTitle("Rectangular cells")
                warning_box.setIcon(QMessageBox.Icon.Question)
                warning_box.addButton(QPushButton("Apply square grid"), QMessageBox.ButtonRole.ApplyRole)
                warning_box.setStandardButtons(QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
                warning_box.setText("With the current grid configuration, the cells in the grid will NOT be square.\nWould you like to continue anyway?")
                user_input = warning_box.exec() # either continue
                if user_input == QMessageBox.StandardButton.No: # dont run sim
                    return
                if user_input != QMessageBox.StandardButton.Yes: # apply correct ratio and don't run sim
                    print("dsffdas")
                    self.correct_grid_ratio()
                    return
            speed = self.pathfinding_speed.value() * 20
            pathfinderSimulation.run(row, col, speed)

        except Exception as e:
            traceback.print_exc()

    def correct_grid_ratio(self):
        print("asdffsad")
        width, height = self.width(), self.height()
        row_field, col_field = self.pathfinding_rows, self.pathfinding_cols
        gcd = np.gcd(width, height)

        cols, rows = width // gcd, height // gcd
        print(rows, cols)
        while rows < 15 or cols < 15:
            rows *= 2
            cols *= 2
        if rows > 100 or cols > 100:
            rows, cols = 18, 32 # default values as square grid can't be made
        self.pathfinding_rows.setValue(rows)
        self.pathfinding_cols.setValue(cols)


    def run_suspension_sim(self):
        try:
            test.run()
        except Exception as e:
            print(e)


    def particleSim(self):
        try:
            idealGasLawSimulation.run()
        except Exception as e:
            print(e)


    def brokenSim(self):
        try:
            fluidFlowSimulation.run()
        except Exception as e:
            print(e)


    def keyPressEvent(self, event):
        if event.key() == 16777217:
            self.ideal_gas_layout.setCurrentIndex((self.ideal_gas_layout.currentIndex() + 1) % len(self.slides))

    def initialise_program(self, user_settings):
        self.penetration_factor_button = QSpinBox()
        self.penetration_factor_button.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.penetration_factor_button.setMaximumWidth(180)
        self.penetration_factor_button.setSuffix("%")
        self.penetration_factor_button.setRange(1, 100)
        self.penetration_factor_button.setValue(15)

        if self.teacher_id is None:
            self.projectile_instruction.setText(
                self.projectile_instruction.text() + "\nTeachers can use the spinbox to control the penetration factor!")
            self.weeklyButton.setMaximumWidth(350)
            self.projectile_widget_layout.addWidget(self.weeklyButton, 2, 2, 1, 1)
            max_level = len(self.projectile_sim_buttons)
            self.projectile_widget_layout.addWidget(self.penetration_factor_button, 2, 1, 1, 1)
        else:
            self.weeklyButton.setFixedWidth(750)
            self.projectile_widget_layout.addWidget(self.weeklyButton, 2, 1, 1, 2)
            max_level = user_settings[-1]

        print(user_settings)
        self.pathfinding_rows.setValue(user_settings[2])
        self.pathfinding_cols.setValue(user_settings[3])
        self.pathfinding_speed.setValue(user_settings[5])

        for index, button in enumerate(self.projectile_sim_buttons[:max_level]):
            self.enable_projectile_button(button, index)




    def enable_projectile_button(self, button, index=-1):
        print(index)
        button.setCheckable(True)
        if index >= 0:
            button.released.connect(lambda index=index: self.run_projectile_motion_sim(index + 1))
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        button.setObjectName("free_button")
        button.setStyleSheet("""
            QPushButton:hover{
                background-color: #83f28f;
            } """)

    def nextSlide(self):
        print()

    def log_off(self):
        print(self.user_settings)
        self.user_settings = list(self.user_settings)
        print(self.user_settings.copy())
        print("Poo")
        try:
            max_level = 1
            for index, button in enumerate(self.projectile_sim_buttons):
                print(button.objectName())
                if button.objectName() == "free_button":
                    max_level = index + 1
            self.user_settings[-1] = max_level
            self.user_settings[2] = int(self.pathfinding_rows.value())
            self.user_settings[3] = int(self.pathfinding_cols.value())
            self.user_settings[5] = int(self.pathfinding_speed.value())

            self.database.save_and_shut_down(self.user_settings)

            self.close()
        except Exception as e:
            traceback.print_exc()

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
