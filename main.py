import sys
import numpy as np
from PyQt6.QtWidgets import QMainWindow, QWidget, QStackedLayout, QToolBar, QGridLayout, QLabel, QLineEdit, QPushButton, \
    QDateEdit, QComboBox, QTableWidget, QSizePolicy, QSpinBox, QSlider, QMessageBox, QApplication, QTableWidgetItem
from PyQt6.QtGui import QFont, QColor, QAction, QCursor, QBrush
from PyQt6.QtCore import Qt, QDate
from Simulations import pathfinderSimulation, projectileMotionSimulation, idealGasLawSimulation, fluidFlowSimulation
from database import Database
from hashlib import sha256
import re


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_info = None
        self.user_settings = None
        self.teacher_id = None
        self.database = Database("localhost", "root", "2121", "NEA")  # Readying database
        self.setWindowTitle("Physics Simulator")
        self.layout = QStackedLayout()
        self.index = QWidget()
        self.index.setLayout(self.layout)
        self.setCentralWidget(self.index)
        self.toolbar = QToolBar()  # How the user navigates the UI
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(False)
        self.toolbar.hide()  # User can not interact with program until successful login
        self.showFullScreen()  # The program is the focus
        self.setFont(QFont("Helvetica", 15))

        self.login_layout = QGridLayout()
        self.login = QWidget()
        self.login.setLayout(self.login_layout)
        self.login.setAutoFillBackground(True)  #
        palette = self.login.palette()  #
        palette.setColor(self.login.backgroundRole(), QColor(255, 249, 196))
        self.login.setPalette(palette)

        self.login_label = QLabel("Physics Simulator")
        self.login_label.setStyleSheet("""
        font-family: 'Times New Roman';
        font-size: 100px;""")
        self.login_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_layout.addWidget(self.login_label, 0, 2, 1, 2)

        self.email = QLineEdit()  # Email field
        self.email.setPlaceholderText("Enter email address")
        self.email.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_layout.addWidget(self.email, 7, 0, 1, 6)

        self.password = QLineEdit()  # Password field
        self.password.setPlaceholderText("Enter password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_layout.addWidget(self.password, 8, 0, 1, 6)

        self.login_button = QPushButton("Log in")  # Log in button
        self.login_button.released.connect(self.login_or_register)
        self.login_button.setMaximumWidth(350)
        self.login_layout.addWidget(self.login_button, 9, 3, 1, 1)

        self.toggle_login = QPushButton("Don't Have\nAn Account?")
        self.toggle_login.setMaximumWidth(350)
        self.toggle_login.released.connect(self.toggle_login_register)
        self.login_layout.addWidget(self.toggle_login, 9, 2, 1, 1)

        # Registration widgets
        self.full_name = QLineEdit()  # Name field
        self.full_name.setPlaceholderText("Enter your full name")
        self.full_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_layout.addWidget(self.full_name, 4, 1, 1, 4)
        self.full_name.hide()

        self.date_of_birth = QDateEdit()  # Birth date field
        self.date_of_birth.setDisplayFormat("dd/MM/yyyy")
        self.date_of_birth.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.date_of_birth.setCalendarPopup(True)
        self.login_layout.addWidget(self.date_of_birth, 6, 1, 1, 2)
        self.date_of_birth.hide()

        self.date_of_birth_label = QLabel("Date of Birth")
        self.login_layout.addWidget(self.date_of_birth_label, 6, 1, 1, 1)
        self.date_of_birth_label.hide()

        teachers = []
        for record in self.database.get_teacher_names():  # Class selection
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

        # Home / Sign Out Page
        self.home_page_button = QAction("Home Page")
        self.toolbar.addAction(self.home_page_button)
        self.toolbar.addSeparator()
        self.home_page_button.triggered.connect(lambda: self.changeIndex(1))

        self.home_page_layout = QGridLayout()
        self.home_page = QWidget()
        self.home_page.setLayout(self.home_page_layout)

        self.home_page.setAutoFillBackground(True)  # Setting background colour
        palette = self.home_page.palette()
        palette.setColor(self.home_page.backgroundRole(), QColor(249, 247, 243))
        self.home_page.setPalette(palette)

        self.home_page.setStyleSheet("""
        QTableWidget {
            font-family: 'Comic Sans MS';
            font-size: 45px;
            padding: 20px;
            border: 0px solid;
        }
        
        QPushButton {
            font-size: 65px;
            padding: 20px;
            color: red;
            border-radius: 20%;
            display: inline-block;
            position: fixed;
            margin: 30px;
            border: 3px solid;
            background-color: '#d7ffcc';
            font-family: 'Comic Sans MS';
        }
        
        QPushButton:hover {background-color: '#abff94';}
        
        QLabel {
            font-family: 'Comic Sans MS';
            color: '#32a142';
            font-size: 40px;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border: none;
        }
        """)
        self.logoff_button = QPushButton("Log Out")  # Exits the program
        self.logoff_button.setFixedSize(700, 300)
        self.logoff_button.released.connect(self.log_off)
        self.home_page_layout.addWidget(self.logoff_button, 1, 0, 1, 1)

        self.projectile_leaderboard_label = QLabel("Projectile Motion\nWeekly Leaderboard")
        self.home_page_layout.addWidget(self.projectile_leaderboard_label, 0, 1)
        self.weeklyScore = 0  # Score is from projectile motion weekly level
        self.projectile_leaderboard = QTableWidget()
        self.projectile_leaderboard.setColumnCount(3)
        self.projectile_leaderboard.setHorizontalHeaderLabels(["Ranking", "Full Name", "Score"])
        self.projectile_leaderboard.verticalHeader().setVisible(False)
        self.projectile_leaderboard.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.projectile_leaderboard.setAlternatingRowColors(True)
        self.projectile_leaderboard.setMinimumHeight(460)
        self.projectile_leaderboard.setColumnWidth(1, 120)
        self.projectile_leaderboard.setStyleSheet("background-color: transparent;")
        header = self.projectile_leaderboard.horizontalHeader()
        header.setStyleSheet(
            "QHeaderView::section { background-color: lightblue; color: white; font-weight: bold; font-size: 45px}")
        self.layout.addWidget(self.home_page)

        # Projectile Motion Simulation
        self.projectile_button = QAction("Projectile Motion", self)
        self.toolbar.addAction(self.projectile_button)
        self.projectile_button.triggered.connect(lambda: self.changeIndex(2))
        self.projectile_widget_layout = QGridLayout()
        self.projectile_widget = QWidget()

        self.projectile_widget.setAutoFillBackground(True)  # Setting background colour
        palette = self.projectile_widget.palette()  #
        palette.setColor(self.projectile_widget.backgroundRole(), QColor(232, 179, 220))
        self.projectile_widget.setPalette(palette)

        self.projectile_widget.setStyleSheet("""
            QLineEdit {
                margin: 60;
                border: 3px solid '#0000ff';
            }

            
            QLabel {
                font-family: 'Comic Sans MS';
                font-size: 29px;
                margin-bottom: 10px;
                padding-bottom: 10px;
                border: none;
            }
            QPushButton, QSpinBox {
                font-family: 'Comic Sans MS';
                font-size: 30px;
                padding: 20px 32px;
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

        self.air_resistance_button = QPushButton("Air Resistance\nENABLED")  # Air resistance button
        self.toggle_air_resistance_button()
        self.air_resistance_button.setMaximumWidth(240)
        self.air_resistance_button.released.connect(self.toggle_air_resistance_button)
        self.air_resistance_button.setCheckable(True)
        self.projectile_widget_layout.addWidget(self.air_resistance_button, 2, 0, 1, 1)

        self.projectile_instruction = QLabel()  # Instructions text
        self.projectile_instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.projectile_instruction.setWordWrap(True)
        self.projectile_instruction.setText("""Welcome to the
Projectile Motion Simulation!   
The aim of the game is to fire the ball into the target. 
The closer to the centre you are, the more score! 
Use SUVAT equations to calculate the required velocity.    
Get 100 score to unlock the next level. 
    
Controls:   
LMB to move the ball    
RMB to project the ball 
t: show parameters table    
v: toggle velocity view 
q: quit""")
        self.projectile_widget_layout.addWidget(self.projectile_instruction, 0, 0, 2, 3)

        self.layout.addWidget(self.projectile_widget)

        # Vector Field Pathfinding Simulation
        self.pathfinding_button = QAction("Vector Field Pathfinding", self)
        self.toolbar.addAction(self.pathfinding_button)
        self.pathfinding_button.triggered.connect(lambda: self.changeIndex(3))
        self.pathfinding_layout = QGridLayout()
        self.pathfinding = QWidget()

        self.pathfinding.setAutoFillBackground(True)  # Setting background colour
        palette = self.pathfinding.palette()
        palette.setColor(self.pathfinding.backgroundRole(), QColor(209, 245, 255))
        self.pathfinding.setPalette(palette)

        self.pathfinding.setStyleSheet("""
            QLabel{
                font-family: 'Comic Sans MS';
                font-size: 30px;
                color: '#000000';
                align: left;
            }
  
            QPushButton, QSpinBox, QSlider{
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
        """)

        self.pathfinding_rows = QSpinBox()  # no of rows for simulation
        self.pathfinding_rows.setRange(4, 100)
        self.pathfinding_rows.setMaximumWidth(300)
        self.pathfinding_layout.addWidget(self.pathfinding_rows, 0, 1)
        pathfinder_rows_label = QLabel("No. of Rows")
        pathfinder_rows_label.setMaximumWidth(400)
        self.pathfinding_layout.addWidget(pathfinder_rows_label, 0, 0)

        self.pathfinding_cols = QSpinBox()  # no of cols for simulation
        self.pathfinding_cols.setRange(4, 100)
        self.pathfinding_cols.setMaximumWidth(300)
        self.pathfinding_layout.addWidget(self.pathfinding_cols, 1, 1)
        pathfinder_columns_label = QLabel("No. of Columns")
        pathfinder_columns_label.setMaximumWidth(400)
        self.pathfinding_layout.addWidget(pathfinder_columns_label, 1, 0)

        self.pathfinding_speed = QSlider()  # desired velocity magnitude for steering behaviour in simulation
        self.pathfinding_speed.setOrientation(Qt.Orientation.Horizontal)
        self.pathfinding_speed.setMaximumWidth(1300)
        self.pathfinding_speed.setRange(1, 100)
        self.pathfinding_speed.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.pathfinding_layout.addWidget(self.pathfinding_speed, 2, 1, 1, 1)

        self.pathfinding_speed_label = QLabel(f"Particle speed = {self.pathfinding_speed.value()}")
        self.pathfinding_speed_label.setFixedWidth(350)
        self.pathfinding_speed.valueChanged.connect(
            lambda: self.pathfinding_speed_label.setText(f"Particle speed = {self.pathfinding_speed.value()}"))
        self.pathfinding_layout.addWidget(self.pathfinding_speed_label, 2, 0, 1, 1)

        self.pathfinding_run = QPushButton("Run")  # Run the pathfinder
        self.pathfinding_run.setMinimumHeight(100)
        self.pathfinding_layout.addWidget(self.pathfinding_run, 3, 1, 1, 3)
        self.pathfinding_run.released.connect(self.run_pathfinder)

        self.pathfinder_instruction = QLabel()  # Instructions text
        self.pathfinder_instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pathfinder_instruction.setWordWrap(True)
        self.pathfinder_instruction.setText("""Welcome to the
        Vector Field Pathfinder!   
        Build mazes, obstacles, and paths... 
        The particles will find their way to the goal! 

        Controls:   
        LMB: Set the goal
        a: Change between the obstacle toggle and adding particles
        RMB: Change cells into obstacles, or vice versa
        RMB|alternative: Add particles! Use the + and - key to change their size!
        c: Enable collisions! Turn this off if the program is slow
        g: Show grid information
        h: Show distance heatmap
        r: Clear the field off all obstacle
        q: Quit""")

        self.pathfinding_layout.addWidget(self.pathfinder_instruction, 0, 2, 2, 3)
        self.pathfinding.setLayout(self.pathfinding_layout)
        self.layout.addWidget(self.pathfinding)

        # Ideal Gas Law Simulation
        self.ideal_gas_button = QAction("Ideal Gas Simulation", self)
        self.toolbar.addAction(self.ideal_gas_button)
        self.ideal_gas_button.triggered.connect(lambda: self.changeIndex(4))
        self.ideal_gas_layout = QGridLayout()
        self.ideal_gas = QWidget()
        self.ideal_gas.setLayout(self.ideal_gas_layout)
        self.layout.addWidget(self.ideal_gas)

        self.ideal_gas.setAutoFillBackground(True)  # Setting background colour
        palette = self.ideal_gas.palette()
        palette.setColor(self.ideal_gas.backgroundRole(), QColor(200, 249, 202))
        self.ideal_gas.setPalette(palette)

        self.ideal_gas.setStyleSheet("""
                    QLineEdit {
                        margin: 60;
                        border: 3px solid '#00ff00';
                    }

                    QPushButton {
                        background-color: '#7AF0B7';
                        font-family: 'Comic Sans MS';
                        font-size: 30px;
                        padding: 20px;
                        margin: 30px;
                        color: '#6B5E62';
                        border-radius: 6%;
                        display: inline-block;
                        position: fixed;
                        transition: 0.4s;
                        border: 3px solid;
                    }

                    QPushButton:hover {
                        background-color: '#83f28f';
                        color: white;
                    }""")

        self.ideal_gas_run = QPushButton("Run ideal gas simulation")  # Runs the simulation
        self.ideal_gas_run.released.connect(self.run_ideal_gas_sim)
        self.ideal_gas_run.setMinimumHeight(150)
        self.ideal_gas_layout.addWidget(self.ideal_gas_run, 3, 1, 1, 1)

        self.ideal_gas_instruction = QLabel()
        self.ideal_gas_instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ideal_gas_instruction.setWordWrap(True)
        self.ideal_gas_instruction.setText("""Welcome to the
Ideal Gas Simulation!   
PV = nRT
Change the conditions and watch how the pressure
and the particles react!

Controls:   
Drag the walls to change the volume of the container!
Click inside the container to add a particle!
Use the buttons!
q: Quit""")
        self.ideal_gas_layout.addWidget(self.ideal_gas_instruction, 0, 0, 2, 3)

        # General stylesheet
        self.setStyleSheet("""
            QLabel{
                font-family: 'Comic Sans MS';
                font-size: 30px;
            }""")

    def changeIndex(self, newIndex):  # Switch between layers
        self.layout.setCurrentIndex(newIndex)

    def attempt_login(self):  # Send data to database and fetch user information
        email, password = self.email.text().strip(), sha256(self.password.text().encode()).hexdigest()
        user_info = self.database.verify_login(email, password)
        if user_info:
            self.user_info = user_info  # Get user information like email and name
            self.user_settings = self.database.get_user_settings(self.user_info[0])  # Get user settings from user id

            if not user_info[-1]:  # If is_teacher field is False:
                self.teacher_id = self.database.get_teacher_id_by_user_id(self.user_info[0])
            else:  # User is a teacher
                self.teacher_id = None

            self.initialise_program()  # Prepare simulation with the user settings
            self.show_toolbar()  # User now has access to simulations
            self.changeIndex(1)  # Switch to the home / sign out page
            return True

        else:
            print(email, password)
            QMessageBox.critical(self, "Verification Failed", "Invalid email or password")
            return False

    def login_or_register(self):
        if self.toggle_login.text()[0] == "A":
            self.create_new_db_user()
        else:
            self.attempt_login()

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

            assert valid  # Ensure that fields have passed validation
            teacher = self.database.get_teacher_email_by_name(self.teacher_dropdown.currentText())  # Get teacher_id
            user_created = self.database.create_user(self.email.text(),
                                                     sha256(self.password.text().encode()).hexdigest(),
                                                     self.full_name.text(),
                                                     self.date_of_birth.date().toString("yyyy-MM-dd"),
                                                     teacher_email=teacher)
            if not user_created:  # If database-side issue, then call an error
                raise AssertionError

            self.toggle_login_register()  # prompt user to login
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
        if self.toggle_login.text()[0] == "A":  # If box says: Already Registered?
            self.toggle_login.setText("Don't have\n an account?")
            self.login_button.setText("Log in")
            self.full_name.hide()
            self.date_of_birth.hide()
            self.date_of_birth_label.hide()
            self.date_of_birth_label.hide()
            self.teacher_dropdown.hide()

        else:  # Switch to Register format
            self.toggle_login.setText("Already have\n an account?")
            self.login_button.setText("Register")
            self.full_name.show()
            self.date_of_birth.show()
            self.date_of_birth_label.show()
            self.teacher_dropdown.show()

    def show_toolbar(self):  # i.e. Enable access to the program and simulations
        self.toolbar.setVisible(True)

    def initialise_program(self):
        self.penetration_factor_button = QSpinBox()  # Penetration factor for creating projectile motion levels
        self.penetration_factor_button.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.penetration_factor_button.setMaximumWidth(180)
        self.penetration_factor_button.setSuffix("%")
        self.penetration_factor_button.setRange(1, 100)
        self.penetration_factor_button.setValue(15)

        if self.teacher_id is None:  # No teacher_id means user is a teacher
            self.projectile_instruction.setText(
                self.projectile_instruction.text() + "\nTeachers can use the spinbox to control the penetration factor!")
            self.weeklyButton.setMaximumWidth(350)
            self.projectile_widget_layout.addWidget(self.weeklyButton, 2, 2, 1, 1)
            max_level = len(self.projectile_sim_buttons)
            self.projectile_widget_layout.addWidget(self.penetration_factor_button, 2, 1, 1, 1)
        else:  # Do not add the projectile_factor_button to the layout
            self.weeklyButton.setFixedWidth(750)
            self.projectile_widget_layout.addWidget(self.weeklyButton, 2, 1, 1, 2)
            max_level = self.user_settings[-1]

        self.pathfinding_rows.setValue(self.user_settings[2])
        self.pathfinding_cols.setValue(self.user_settings[3])
        self.pathfinding_speed.setValue(self.user_settings[4])
        self.weeklyScore = self.user_settings[5]
        if self.weeklyScore > 0:
            self.weeklyButton.setText(f"Level of the Week\nCurrent Score: {self.weeklyScore}")
        self.fill_projectile_leaderboard()  # Projectile motion weekly leaderboard
        for index, button in enumerate(self.projectile_sim_buttons[:max_level]):
            self.enable_projectile_button(button, index)

    def fill_projectile_leaderboard(self):
        row_count = 10
        self.projectile_leaderboard.clearContents()
        teacher_id = self.teacher_id
        if self.teacher_id is None:
            teacher_id = self.database.get_teachers_teacher_id(self.user_info[0])
            print("teacher_id: ", teacher_id)
        fields = self.database.get_projectile_rankings(teacher_id)
        self.projectile_leaderboard.setRowCount(row_count + 1)

        for index, (name, score) in enumerate(fields[:row_count]):  # Fill the leaderboard with fetched data
            print(index, name, score)
            record = (QTableWidgetItem(str(index + 1)), QTableWidgetItem(name), QTableWidgetItem(str(score)))
            for column, item in enumerate(record):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFont(QFont("Comic Sans MS", 25))
                self.projectile_leaderboard.setItem(index, column, item)

        user_record = (
            QTableWidgetItem("-"), QTableWidgetItem(self.user_info[3]), QTableWidgetItem(str(self.weeklyScore)))
        for column, item in enumerate(user_record):  # Have the last row as the user's score
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFont(QFont("Comic Sans MS", 25))
            item.setBackground(QBrush(QColor(80, 30, 50, 125)))
            self.projectile_leaderboard.setItem(row_count, column, item)

        self.home_page_layout.addWidget(self.projectile_leaderboard, 1, 1, 2, 1)

    def enable_projectile_button(self, button, index=-1):  # Buttons are disabled by default
        button.setCheckable(True)
        if index >= 0:
            button.released.connect(lambda index=index: self.run_projectile_motion_sim(index + 1))
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        button.setObjectName("free_button")
        button.setStyleSheet("""
            QPushButton:hover{
                background-color: #83f28f;
            } """)

    def toggle_air_resistance_button(self):
        text = self.air_resistance_button.text()
        if "DISABLED" in text:  # Then enable air resistance
            self.air_resistance_button.setText("Air Resistance\nENABLED")
            self.air_resistance_button.setStyleSheet("""
            QPushButton {
            font-family: 'Times New Roman';
            background-color: rgba(0, 255, 0, 0.3);
            color: black;
            } """)
        else:  # Then disable air resistance
            self.air_resistance_button.setText("Air Resistance\nDISABLED")
            self.air_resistance_button.setStyleSheet("""
            QPushButton {
            font-family: 'Times New Roman';
            background-color: rgba(255, 0, 0, 0.3);
            color: black;
            }""")

    def run_projectile_motion_sim(self, level_no):
        if self.teacher_id is None:
            projectileMotionSimulation.draw_mode(level_no, self.penetration_factor_button.value() / 100)

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
                    self.save_to_database()
                    self.fill_projectile_leaderboard()

    def run_pathfinder(self):
        row = self.pathfinding_rows.value()
        col = self.pathfinding_cols.value()
        if row / col != self.height() / self.width():  # If cells are rectangular
            warning_box = QMessageBox()
            warning_box.setWindowTitle("Rectangular cells")
            warning_box.setIcon(QMessageBox.Icon.Question)
            warning_box.addButton(QPushButton("Apply square grid"), QMessageBox.ButtonRole.ApplyRole)
            warning_box.setStandardButtons(QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
            warning_box.setText(
                "With the current grid configuration, the cells in the grid will NOT be square.\nWould you like to continue anyway?")
            user_input = warning_box.exec()  # Either Yes for continue, No, or No and implement square grid
            if user_input == QMessageBox.StandardButton.No:  # Don't run sim
                return
            if user_input != QMessageBox.StandardButton.Yes:  # Apply square grid and don't run sim
                self.correct_grid_ratio()
                return
        speed = self.pathfinding_speed.value() * 20
        pathfinderSimulation.run(row, col, speed)

    def correct_grid_ratio(self):
        width, height = self.width(), self.height()
        gcd = np.gcd(width, height)  # greatest common denominator
        cols, rows = width // gcd, height // gcd
        while rows < 15 or cols < 15:  # i.e. if the grid is too small as it is
            rows *= 2
            cols *= 2
        if rows > 100 or cols > 100:  # If the screen size is such that the smallest grid size is impractical
            rows, cols = 18, 32  # Simply apply a default grid size of 18x32
        self.pathfinding_rows.setValue(rows)
        self.pathfinding_cols.setValue(cols)

    def run_ideal_gas_sim(self):
        try:
            idealGasLawSimulation.run()
        except Exception as e:
            print(e)

    def run_fluid_flow_sim(self):
        try:
            fluidFlowSimulation.run()
        except Exception as e:
            print(e)

    def log_off(self):
        self.save_to_database()
        self.close()

    def save_to_database(self):
        print(self.user_settings)
        self.user_settings = list(self.user_settings)

        max_level = 1
        for index, button in enumerate(self.projectile_sim_buttons):
            print(button.objectName())
            if button.objectName() == "free_button":
                max_level = index + 1
        self.user_settings[-1] = max_level
        self.user_settings[2] = int(self.pathfinding_rows.value())
        self.user_settings[3] = int(self.pathfinding_cols.value())
        self.user_settings[4] = int(self.pathfinding_speed.value())
        self.user_settings[5] = int(self.weeklyScore)
        print(self.user_settings, "new ")

        self.database.save_and_shut_down(self.user_settings)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
