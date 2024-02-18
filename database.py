import mysql.connector

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
            self.conn.fetchall()  # fetching everytime to debug, will change later

            self.conn.execute("""
            DROP TABLE IF EXISTS users;
            """)
            self.conn.fetchall()

            self.conn.execute("""
            CREATE TABLE users (
                id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                email VARCHAR(256) UNIQUE NOT NULL,
                password_hash CHAR(64) NOT NULL,
                full_name VARCHAR(64),
                date_of_birth DATE 
            );
            """)
            self.conn.fetchall()

            self.conn.execute("""
            CREATE TABLE user_settings (
                id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                pathfinder_heatmap BOOLEAN DEFAULT FALSE,
                pathfinder_grid BOOLEAN DEFAULT FALSE,
                pathfinder_rows INT DEFAULT 20,
                pathfinder_cols INT DEFAULT 20,
                wall_collision_damping FLOAT DEFAULT 0.8,
                particle_collision_damping FLOAT DEFAULT 1.0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)
            self.conn.fetchall()

            self.conn.execute("""
            INSERT INTO users (email, password_hash, full_name, date_of_birth) VALUES 
            ('email@email.com', 'password', 'First Last', '2000-01-01'),
            ('passwordGimp@email.com', 'passwordGimp Gimp', 'Grinch', '1975-05-10'),
            ('SamVokes@gmail.com', 'passwordGuppy', 'Sam Vokes', '2006-04-28');
            """)
            self.conn.fetchall()  # Fetch the results before executing another query

            self.conn.execute("""
            INSERT INTO user_settings (user_id, pathfinder_rows, pathfinder_cols) VALUES
            (1, 30, 30),
            (2, 32, 18),
            (3, 15, 15);
            """)
            self.conn.fetchall()

            print("Database initialised successfully.")
        except Exception as e:
            print("Error initialising database:", e)

    def create_user(self, email, password_hash, full_name, date_of_birth):
        try:
            self.conn.execute("""
            INSERT INTO users (email, password_hash, full_name, date_of_birth) VALUES (%s, %s, %s, %s);
            """, (email, password_hash, full_name, date_of_birth))
            self.conn.fetchall()  # Fetch results after executing each query


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
            result = self.conn.fetchall()
            return result
        except Exception as e:
            print("\nError verifying login", email, password_hash)
            print(e)
            return None

    def get_user_settings(self, user_id):
        self.conn.execute("""
        SELECT * FROM user_settings WHERE user_id = %s;
        """, (user_id,))
        result = self.conn.fetchall()
        return result

    def save_user_settings(self, user_id, settings):
        self.conn.execute("""
        UPDATE user_settings SET pathfinder_heatmap = %s, pathfinder_grid = %s, pathfinder_rows = %s, pathfinder_cols = %s, wall_collision_damping = %s, particle_collision_damping = %s WHERE user_id = %s;
        """, settings + (user_id,))






if __name__ == "__main__":
    db = Database("localhost", "root", "2121", "NEA")
    # db.initialise_default_db()

    try:
        db.conn.execute("SELECT * FROM users")
        results = db.conn.fetchall()
        for row in results:
            print(row)
    except Exception as e:
        print("Error:", e)
