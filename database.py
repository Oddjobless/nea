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
        self.conn.execute("""
        DROP TABLE IF EXISTS user_settings;
        
        DROP TABLE IF EXISTS users;
        
        CREATE TABLE users (
            id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
            email VARCHAR(256) UNIQUE NOT NULL,
            password_hash CHAR(64) NOT NULL,
            full_name VARCHAR(64),
            date_of_birth DATE 
        );

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
        

        INSERT INTO users (email, password_hash, full_name, date_of_birth) VALUES 
        ('email@email.com', 'password', 'First Last', '2000-01-01'),
        ('passwordGimp@email.com', 'passwordGimp Gimp', 'Grinch', '1975-05-10'),
        ('SamVokes@gmail.com', 'passwordGuppy', 'Sam Vokes', '2006-04-28');

        INSERT INTO user_settings (user_id, pathfinder_rows, pathfinder_cols) VALUES
        (1, 30, 30),
        (2, 32, 18),
        (3, 15, 15);
        """)

        #max length for email is 255 characters apparently

    def create_user(self, email, password_hash, full_name, date_of_birth):
        try:
            self.conn.execute("""
            INSERT INTO users (email, password_hash, full_name, date_of_birth) VALUES (%s, %s, %s, %s);
            INSERT INTO user_settings (user_id) VALUES (LAST_INSERT_ID());
            """, (email, password_hash, full_name, date_of_birth))
            return True
        except:
            print(email, password_hash, full_name, date_of_birth)
            return False

    def verify_login(self, email, password_hash):
        self.conn.execute("""
        SELECT * FROM users WHERE email = %s AND password_hash = %s;
        """, (email, password_hash))
        return self.conn.fetchone()

    def get_user_settings(self, user_id):
        self.conn.execute("""
        SELECT * FROM user_settings WHERE user_id = %s;
        """, (user_id,))
        return self.conn.fetchone()

    def save_user_settings(self, user_id, settings):
        self.conn.execute("""
        UPDATE user_settings SET pathfinder_heatmap = %s, pathfinder_grid = %s, pathfinder_rows = %s, pathfinder_cols = %s, wall_collision_damping = %s, particle_collision_damping = %s WHERE user_id = %s;
        """, settings + (user_id,))






if __name__ == "__main__":
    db = Database("localhost", "root", "2121", "NEA")
    db.initialise_default_db()

    # db.conn.execute("SELECT * FROM users")
    print(db.conn.fetchall())
