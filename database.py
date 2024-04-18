import mysql.connector


class Database:
    def __init__(self, host_, user_, password_, database_):  # Connect to the server
        self.__db = mysql.connector.connect(
            host=host_,
            user=user_,
            password=password_,
            database=database_,
            autocommit=True
        )

        self.__conn = self.__db.cursor()

    def initialise_default_db(self):
        try:
            # Removing old tables
            self.__conn.execute("DROP TABLE IF EXISTS user_settings;")
            self.__conn.execute("DROP TABLE IF EXISTS students;")
            self.__conn.execute("DROP TABLE IF EXISTS teachers;")
            self.__conn.execute("DROP TABLE IF EXISTS users;")

            # Creating new tables
            self.__conn.execute("""
            CREATE TABLE users (
                user_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                email VARCHAR(256) UNIQUE NOT NULL,
                password_hash CHAR(64) NOT NULL,
                full_name VARCHAR(64),
                date_of_birth DATE,
                is_teacher BOOLEAN DEFAULT FALSE
            );""")

            self.__conn.execute("""
            CREATE TABLE teachers (
                teacher_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );""")

            self.__conn.execute("""
            CREATE TABLE students (
                student_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                teacher_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
            );""")

            self.__conn.execute("""
            CREATE TABLE user_settings (
                id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                pathfinder_rows INT DEFAULT 18,
                pathfinder_cols INT DEFAULT 32,
                pathfinding_velocity INT DEFAULT 40,
                projectile_score INT DEFAULT 0,
                projectile_max_level INT DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );""")

            # Creating teachers and a couple student account for placeholders
            self.create_user("admin", "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8", "No class",
                             "2000-01-01", is_teacher=True)  # password
            self.create_user("teacher@email.com", "1057a9604e04b274da5a4de0c8f4b4868d9b230989f8c8c6a28221143cc5a755",
                             "Mr Smith", "2000-01-01", is_teacher=True)  # teacher
            self.create_user("m.stevens@gmail.com", "16a3a923a6143b7b1ebc73ea64ef23fc41ed7b26b883f51c8e90bb32a9cb3dc4",
                             "Mr Stevens", "2000-01-01", is_teacher=True)  # stevens
            self.create_user("student", "placeholder", "student1", "2000-01-01", teacher_email="m.stevens@gmail.com")
            self.create_user("student1", "placeholder", "student2", "2000-01-01", teacher_email="m.stevens@gmail.com")
            print("Database initialised successfully.")

        except Exception as e:
            print("Error initialising database:", e)

    def create_user(self, email, password_hash, full_name, date_of_birth, is_teacher=False, teacher_email=None):
        # Create either a student or a teacher account
        try:
            if not is_teacher:  # Get teacher_id from email and then perform pseudocode
                teacher_id = self.get_teacher_id(teacher_email)

            self.__conn.execute("""
            INSERT INTO users (email, password_hash, full_name, date_of_birth, is_teacher) VALUES (%s, %s, %s, %s, %s);
            """, (email, password_hash, full_name, date_of_birth, is_teacher))

            user_id = self.__conn.lastrowid
            self.__conn.execute("""
            INSERT INTO user_settings (user_id) VALUES (%s);
            """, (user_id,))

            if is_teacher:
                self.__conn.execute("INSERT INTO teachers (user_id) VALUES (%s);", (user_id,))
            else:  # Is a student
                self.__conn.execute("INSERT INTO students (user_id, teacher_id) VALUES (%s, %s);", (user_id, teacher_id))
            return True

        except:
            print("Could not create user")
            return False

    def get_teacher_id(self, email):  # Get teacher_id from their email address
        self.__conn.execute("""
        SELECT user_id FROM users WHERE email = %s;
        """, (email,))
        result = self.__conn.fetchone()
        if result is None:
            print("Teacher not in database")
            return None
        return result[0]

    def get_teacher_email_by_name(self, name):
        self.__conn.execute("""
        SELECT email FROM users WHERE full_name = %s;
        """, (name,))
        result = self.__conn.fetchone()
        if result is None:
            print("Teacher not in database")
            return None
        return result[0]

    def get_teachers_teacher_id(self, user_id):  # Get teacher_id of a teacher via user_id
        self.__conn.execute("""
        SELECT teachers.teacher_id 
        FROM users, teachers 
        WHERE users.user_id = %s AND users.user_id = teachers.user_id; 
        """, (user_id,))
        result = self.__conn.fetchone()
        return result[0]

    def get_projectile_rankings(self, teacher_id):  # Used for projectile motion leaderboard
        self.__conn.execute("""
        SELECT full_name, projectile_score
        FROM users, user_settings, students
        WHERE users.user_id = students.user_id
        AND users.user_id = user_settings.user_id
        AND students.teacher_id = %s
        ORDER BY projectile_score DESC;
        """, (teacher_id,))
        result = self.__conn.fetchall()
        return result

    def get_teacher_names(self):  # Get all teachers for account creation stage
        self.__conn.execute("""
        SELECT full_name FROM users, teachers WHERE users.user_id = teachers.user_id;
        """)
        result = self.__conn.fetchall()
        return result

    def get_teacher_id_by_user_id(self, user_id):  # Get teacher_id of a student
        self.__conn.execute("""
        SELECT teacher_id FROM students WHERE user_id = %s;
        """, (user_id,))
        result = self.__conn.fetchone()
        return result[0]

    def verify_login(self, email, password_hash):
        try:
            self.__conn.execute("""
            SELECT * FROM users WHERE email = %s AND password_hash = %s;
            """, (email, password_hash))
            result = self.__conn.fetchone()
            assert result is not None
            return result
        except AssertionError:
            print("Incorrect login details")
            return None
        except:
            print("Unexpected error when verifying login")
            return None

    def get_user_settings(self, user_id):  # Fetch the user settings from the according user_id
        self.__conn.execute("""
        SELECT * FROM user_settings WHERE user_id = %s;
        """, (user_id,))
        result = self.__conn.fetchone()
        return result

    def save_and_shut_down(self, user_settings):  # Save new settings to the database
        settings = user_settings.copy()
        settings.append(settings[0])
        self.__conn.execute("""
        UPDATE user_settings SET pathfinder_rows = %s, pathfinder_cols = %s, pathfinding_velocity = %s, projectile_score = %s, projectile_max_level = %s WHERE user_id = %s;
        """, settings[2:])


if __name__ == "__main__":
    db = Database("localhost", "root", "2121", "NEA")
    db.initialise_default_db()