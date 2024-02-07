import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2121",
    database="employees"
)

conn = db.cursor()

def create_boilerplate_db():
    conn.execute("""
    DROP DATABASE IF EXISTS employees;
    CREATE DATABASE IF NOT EXISTS employees;
    USE employees;
    
    SELECT 'CREATING DATABASE STRUCTURE' as 'INFO';
    
    DROP TABLE IF EXISTS employees,
                         departments;
    
    /*!50503 set default_storage_engine = InnoDB */;
    /*!50503 select CONCAT('storage engine: ', @@default_storage_engine) as INFO */;
    
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

conn.execute("SELECT first_name, last_name FROM employees WHERE gender = 'M'")
print(conn.fetchall())