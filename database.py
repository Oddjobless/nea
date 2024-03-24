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
        self.db = mysql.connector.connect(
            host=host_,
            user=user_,
            password=password_,
            database=database_,
            autocommit=True
        )

        self.conn = self.db.cursor()

    def initialise_default_db(self):
        try:
            self.conn.execute("""
            DROP TABLE IF EXISTS user_settings;
            """)
            self.conn.fetchall()

            self.conn.execute("""
            
            DROP TABLE IF EXISTS teachers;
            """)
            self.conn.fetchall()

            self.conn.execute("""
            DROP TABLE IF EXISTS students;
            """)
            self.conn.fetchall()



            self.conn.execute("""
            DROP TABLE IF EXISTS users;
            """)
            self.conn.fetchall()

            self.conn.execute("""
            CREATE TABLE users (
                user_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                email VARCHAR(256) UNIQUE NOT NULL,
                password_hash CHAR(64) NOT NULL,
                full_name VARCHAR(64),
                date_of_birth DATE,
                is_teacher BOOLEAN DEFAULT FALSE
            );
            """)
            self.conn.fetchall()

            self.conn.execute("""
            CREATE TABLE teachers (
                teacher_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            """)
            self.conn.fetchall()

            self.conn.execute("""
            CREATE TABLE students (
                student_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                teacher_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
            );
            """)
            self.conn.fetchall()

            self.conn.execute("""
            CREATE TABLE user_settings (
                id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                pathfinder_rows INT DEFAULT 20,
                pathfinder_cols INT DEFAULT 20,
                wall_collision_damping FLOAT DEFAULT 0.8,
                particle_collision_damping FLOAT DEFAULT 1.0,
                projectile_max_level INT DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            """)
            self.conn.fetchall()

            self.create_user("admin", "21232f297a57a5a743894a0e4a801fc3", "admin", "2000-01-01", is_teacher=True)
            self.create_user("teacher@email.com", "21232f297a57a5a743894a0e4a801fc3", "teacher", "2000-01-01", is_teacher=True)
            self.create_user("student", "21232f297a57a5a743894a0e4a801fc3", "student", "2000-01-01", teacher_email="teacher@email.com")
            self.create_user("student1", "21232f297a57a5a7438", "student", "2000-01-01", teacher_email="teacher@email.com")


            self.conn.fetchall()



            print("Database initialised successfully.")
        except Exception as e:
            print("Error initialising database:", e)

    def create_user(self, email, password_hash, full_name, date_of_birth, is_teacher=False, teacher_email=None):
        try:
            self.conn.execute("""
            SELECT email FROM users, teachers
            WHERE users.user_id = teachers.user_id
            """)
            print(self.conn.fetchall())

            if not is_teacher:
                teacher_id = self.conn.execute("""
                SELECT user_id FROM users WHERE email = %s;
                """, (teacher_email,))
                print(teacher_email)
                teacher_id = self.conn.fetchone()[0]


            self.conn.execute("""
            INSERT INTO users (email, password_hash, full_name, date_of_birth, is_teacher) VALUES (%s, %s, %s, %s, %s);
            """, (email, password_hash, full_name, date_of_birth, is_teacher))
            self.conn.fetchall()

            user_id = self.conn.lastrowid
            self.conn.execute("""
            INSERT INTO user_settings (user_id) VALUES (%s);
            """, (user_id,))
            self.conn.fetchall()

            if is_teacher:
                self.conn.execute("""
                INSERT INTO teachers (user_id) VALUES (%s);
                """, (user_id,))

            else: # is a student

                self.conn.execute("""
                INSERT INTO students (user_id, teacher_id) VALUES (%s, %s);
                """, (user_id, teacher_id))



            print("\n\nUser Created.", email, password_hash)
            return True
        except Exception as e:
            print(email, password_hash, full_name, date_of_birth)
            print("Could not create user")
            print(e)
            return False

    def verify_login(self, email, password_hash):
        try:
            self.conn.execute("""
            SELECT * FROM users WHERE email = %s AND password_hash = %s;
            """, (email, password_hash))
            print("Successful log in")
            result = self.conn.fetchone()
            print(result, "this")
            return result
        except Exception as e:
            print("\nError verifying login", email, password_hash)
            print(e)
            return None

    def get_user_settings(self, user_id):
        self.conn.execute("""
        SELECT * FROM user_settings WHERE user_id = %s;
        """, (user_id,))
        result = self.conn.fetchone()
        return result

    def save_user_settings(self, user_settings):
        settings = user_settings.copy()
        print(settings, "this")

        settings.append(settings[0])
        print(settings)
        print(settings[2:])
        self.conn.execute("""
        UPDATE user_settings SET pathfinder_rows = %s, pathfinder_cols = %s, wall_collision_damping = %s, particle_collision_damping = %s, projectile_max_level = %s WHERE user_id = %s;
        """, settings[2:])
        self.conn.fetchall()






if __name__ == "__main__":
    db = Database("localhost", "root", "2121", "NEA")
    db.initialise_default_db()

    try:

        db.conn.execute("SELECT * FROM users")
        results = db.conn.fetchall()
        for row in results:
            print(row)

        db.conn.execute("SELECT full_name FROM students, teachers WHERE students.teacher_id = teachers.teacher_id AND teachers.user_id = 1")
        results = db.conn.fetchall()
        for row in results:
            print(row)

    except Exception as e:
        print("Error:", e)
