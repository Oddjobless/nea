import mysql.connector
from PyQt6.QtCore import QDate

"""db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2121",
    database="employees"
)

conn = db.cursor()"""


class Database:
    def __init__(self, host_, user_, password_, database_):
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
            self.__conn.execute("""
            DROP TABLE IF EXISTS user_settings;
            """)
            self.__conn.fetchall()

            self.__conn.execute("""
            DROP TABLE IF EXISTS students;
            """)
            self.__conn.fetchall()

            self.__conn.execute("""
            
            DROP TABLE IF EXISTS teachers;
            """)
            self.__conn.fetchall()

            self.__conn.execute("""
            DROP TABLE IF EXISTS users;
            """)
            self.__conn.fetchall()

            self.__conn.execute("""
            CREATE TABLE users (
                user_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                email VARCHAR(256) UNIQUE NOT NULL,
                password_hash CHAR(64) NOT NULL,
                full_name VARCHAR(64),
                date_of_birth DATE,
                is_teacher BOOLEAN DEFAULT FALSE
            );
            """)
            self.__conn.fetchall()

            self.__conn.execute("""
            CREATE TABLE teachers (
                teacher_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            """)
            self.__conn.fetchall()

            self.__conn.execute("""
            CREATE TABLE students (
                student_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                teacher_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
            );
            """)
            self.__conn.fetchall()

            self.__conn.execute("""
            CREATE TABLE user_settings (
                id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                pathfinder_rows INT DEFAULT 18,
                pathfinder_cols INT DEFAULT 32,
                wall_collision_damping FLOAT DEFAULT 0.8,
                pathfinding_velocity INT DEFAULT 500,
                projectile_max_level INT DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            """)
            self.__conn.fetchall()

            self.create_user("admin", "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8", "No class", "2000-01-01", is_teacher=True) # password
            self.create_user("teacher@email.com", "1057a9604e04b274da5a4de0c8f4b4868d9b230989f8c8c6a28221143cc5a755", "Mr Smith", "2000-01-01", is_teacher=True) # teacher
            self.create_user("m.stevens@gmail.com", "16a3a923a6143b7b1ebc73ea64ef23fc41ed7b26b883f51c8e90bb32a9cb3dc4", "Mr Stevens", "2000-01-01", is_teacher=True) # stevens
            self.create_user("student", "placeholder", "student", "2000-01-01", teacher_email="m.stevens@gmail.com")
            self.create_user("student1", "placeholder", "student", "2000-01-01", teacher_email="m.stevens@gmail.com")
            self.create_user("student2", "placeholder", "student", "2000-01-01", teacher_email="m.stevens@gmail.com")
            self.create_user("student3", "placeholder", "student", "2000-01-01", teacher_email="m.stevens@gmail.com")
            self.create_user("student4", "placeholder", "student", "2000-01-01", teacher_email="m.stevens@gmail.com")
            self.create_user("student5", "placeholder", "student", "2000-01-01", teacher_email="m.stevens@gmail.com")
            self.create_user("student6", "placeholder", "student", "2000-01-01", teacher_email="m.stevens@gmail.com")
            self.create_user("student7", "placeholder", "student", "2000-01-01", teacher_email="m.stevens@gmail.com")

            self.__conn.fetchall()



            print("Database initialised successfully.")
        except Exception as e:
            print("Error initialising database:", e)

    def create_user(self, email, password_hash, full_name, date_of_birth, is_teacher=False, teacher_email=None):
        try:
            self.__conn.execute("""
            SELECT email FROM users, teachers
            WHERE users.user_id = teachers.user_id
            """)
            print(self.__conn.fetchall())

            if not is_teacher:
                teacher_id = self.get_teacher_id(teacher_email)


            self.__conn.execute("""
            INSERT INTO users (email, password_hash, full_name, date_of_birth, is_teacher) VALUES (%s, %s, %s, %s, %s);
            """, (email, password_hash, full_name, date_of_birth, is_teacher))
            self.__conn.fetchall()

            user_id = self.__conn.lastrowid
            self.__conn.execute("""
            INSERT INTO user_settings (user_id) VALUES (%s);
            """, (user_id,))
            self.__conn.fetchall()

            if is_teacher:
                self.__conn.execute("""
                INSERT INTO teachers (user_id) VALUES (%s);
                """, (user_id,))

            else: # is a student

                self.__conn.execute("""
                INSERT INTO students (user_id, teacher_id) VALUES (%s, %s);
                """, (user_id, teacher_id))



            print("\n\nUser Created.", email, password_hash)
            return True
        except Exception as e:
            print(email, password_hash, full_name, date_of_birth)
            print("Could not create user")
            print(e)
            return False

    def get_teacher_id(self, email):
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



    def get_teacher_names(self):
        self.__conn.execute("""
        SELECT full_name FROM users, teachers WHERE users.user_id = teachers.user_id;
        """)
        result = self.__conn.fetchall()
        return result

    def get_teacher_id_by_user_id(self, user_id):
        self.__conn.execute("""
        SELECT teacher_id FROM students WHERE user_id = %s;
        """, (user_id,))
        result = self.__conn.fetchone()
        return result

    def get_students_by_teacher_id(self, teacher_id):
        self.__conn.execute("""
        SELECT * FROM users, students WHERE teacher_id = %s AND users.user_id = students.user_id;
        """, (teacher_id,))
        result = self.__conn.fetchall()
        return result
    def verify_login(self, email, password_hash):
        try:
            self.__conn.execute("""
            SELECT * FROM users WHERE email = %s AND password_hash = %s;
            """, (email, password_hash))
            result = self.__conn.fetchone()
            assert result is not None
            return result
        except Exception as e:
            print("\nError verifying login", email, password_hash)
            print(e)
            return None

    def get_all_users(self):
        self.__conn.execute("""
        SELECT * FROM users;
        """)
        result = self.__conn.fetchall()
        return result
    def get_user_settings(self, user_id):
        self.__conn.execute("""
        SELECT * FROM user_settings WHERE user_id = %s;
        """, (user_id,))
        result = self.__conn.fetchone()
        return result

    def save_and_shut_down(self, user_settings):
        settings = user_settings.copy()
        print(settings, "this")

        settings.append(settings[0])
        print(settings)
        print(settings[2:])
        self.__conn.execute("""
        UPDATE user_settings SET pathfinder_rows = %s, pathfinder_cols = %s, wall_collision_damping = %s, pathfinding_velocity = %s, projectile_max_level = %s WHERE user_id = %s;
        """, settings[2:])
        self.__conn.fetchall()







if __name__ == "__main__":
    db = Database("localhost", "root", "2121", "NEA")
    db.initialise_default_db()

    try:

        # print all users
        result = db.get_all_users()
        for row in result:
            print(row)

    except Exception as e:
        print("Error:", e)
