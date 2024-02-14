import mysql.connector

"""db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2121",
    database="employees"
)

conn = db.cursor()"""

def create_boilerplate_db():
    conn.execute("""
    DROP DATABASE IF EXISTS employees;
    CREATE DATABASE IF NOT EXISTS employees;
    USE employees;
    

    
    DROP TABLE IF EXISTS employees,
                         departments;

    
    CREATE TABLE employees (
        emp_no      INT             NOT NULL AUTO_INCREMENT,
        birth_date  DATE            NOT NULL,
        first_name  VARCHAR(14)     NOT NULL,
        last_name   VARCHAR(16)     NOT NULL,
        gender      ENUM ('M','F')  NOT NULL,
        PRIMARY KEY (emp_no)
    );
    
    INSERT INTO employees (birth_date, first_name, last_name, gender) VALUES
        ('1972-05-13','Peter','Diaz','M'),
        ('1987-09-25','Leon','Leonard','M'),
        ('1974-05-10','Shirley','Baker','F'),
        ('1986-08-17','David','Allen','M'),
        ('1959-10-14','Nancy','Davis','F'),
        ('1964-07-05','Michael','Wray','M'),
        ('1980-10-08','Wanda','Inniss','F');
    
    CREATE TABLE departments (
        dept_no     CHAR(4)         NOT NULL,
        dept_name   VARCHAR(40)     NOT NULL,
        manger_no   INT             NOT NULL,
        PRIMARY KEY (dept_no),
        UNIQUE  KEY (dept_name),
        FOREIGN KEY (manger_no) REFERENCES employees (emp_no) ON DELETE CASCADE
    );
    
    INSERT INTO departments VALUES
        ('d001','Marketing', 3),
        ('d002','Finance', 1),
        ('d003','Human Resources', 7);
    
    ALTER TABLE employees
        ADD COLUMN dept_no CHAR(4),
        ADD FOREIGN KEY (dept_no) REFERENCES departments(dept_no) ON DELETE CASCADE;
    
    UPDATE employees
        SET dept_no = 'd001'
        WHERE emp_no IN (3);
    UPDATE employees
        SET dept_no = 'd002'
        WHERE emp_no IN (1, 2);
    UPDATE employees
        SET dept_no = 'd003'
        WHERE emp_no IN (4, 5, 6, 7);
    """)


class Database:
    def __init__(self, user_, password_, host_, database_):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="2121",
            database="employees"
        )

        self.conn = self.db.cursor()

    def initialise__default_db(self):
        self.conn.execute("""DROP DATABASE IF EXISTS NEA;
        CREATE DATABASE IF NOT EXISTS NEA;
        USE NEA;
        
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS user_settings;
        
        CREATE TABLE users (
            id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
            username VARCHAR(32) UNIQUE NOT NULL,
            password_hash CHAR(64) NOT NULL,
            email UNIQUE VARCHAR(256) NOT NULL,
            first_name VARCHAR(32),
            last_name VARCHAR(32),
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
        )
        
        INSERT INTO users VALUES 
        ('username', 'password', 'email@email.com', 'First', 'Last', '2000-01-01');
        ('UnregisteredGimp', 'passwordGimp', 'passwordGimp@email.com', 'Gimp', 'Grinch', '1975-05-10')
        ('FunnyGuppyGaming', 'passwordGuppy', 'SamVokes@gmail.com', 'Sam', 'Vokes', '2006-04-28');
        
        INSERT INTO user_settings (user_id, pathfinder_rows, pathfinder_cols) VALUES
        (1, 30, 30)
        (2, 32, 18)
        (3, 15, 15);
        
        """)




db = Database("root", "2121", "localhost", "employees")
db.initialise_default_db()
