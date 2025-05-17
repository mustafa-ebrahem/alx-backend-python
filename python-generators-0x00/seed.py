#!/usr/bin/python3
"""
Database seeding script for MySQL with generator functionality
"""
import mysql.connector
import csv
import uuid
import os


def connect_db():
    """
    Connects to the MySQL database server
    Returns: MySQL connection object or None if connection fails
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root"
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None


def create_database(connection):
    """
    Creates the database ALX_prodev if it does not exist
    Args:
        connection: MySQL connection object
    """
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        cursor.close()
    except mysql.connector.Error as e:
        print(f"Error creating database: {e}")


def connect_to_prodev():
    """
    Connects to the ALX_prodev database in MySQL
    Returns: MySQL connection object to ALX_prodev or None if connection fails
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None


def create_table(connection):
    """
    Creates a table user_data if it does not exist with the required fields
    Args:
        connection: MySQL connection object to ALX_prodev
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL NOT NULL,
                INDEX (user_id)
            )
        """)
        connection.commit()
        cursor.close()
        print("Table user_data created successfully")
    except mysql.connector.Error as e:
        print(f"Error creating table: {e}")


def insert_data(connection, csv_file):
    """
    Inserts data from a CSV file into the user_data table if it doesn't exist
    Args:
        connection: MySQL connection object to ALX_prodev
        csv_file: Path to the CSV file containing user data
    """
    try:
        # First check if the CSV file exists
        if not os.path.exists(csv_file):
            print(f"CSV file {csv_file} not found")
            return

        cursor = connection.cursor()
        
        # Read the CSV file and insert the data
        with open(csv_file, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row if it exists
            
            for row in csv_reader:
                # Check if we have enough columns
                if len(row) >= 3:
                    # Generate UUID for user_id if not provided
                    user_id = str(uuid.uuid4()) if len(row) < 4 else row[0]
                    name = row[0] if len(row) < 4 else row[1]
                    email = row[1] if len(row) < 4 else row[2]
                    age = row[2] if len(row) < 4 else row[3]
                    
                    # Check if the user already exists
                    cursor.execute(
                        "SELECT user_id FROM user_data WHERE user_id = %s",
                        (user_id,)
                    )
                    exists = cursor.fetchone()
                    
                    if not exists:
                        cursor.execute(
                            """
                            INSERT INTO user_data (user_id, name, email, age)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (user_id, name, email, age)
                        )
        
        connection.commit()
        cursor.close()
    except mysql.connector.Error as e:
        print(f"Error inserting data: {e}")


def row_generator(connection, batch_size=10):
    """
    Generator function that streams rows from the user_data table one by one
    Args:
        connection: MySQL connection object to ALX_prodev
        batch_size: Number of rows to fetch at a time (for efficiency)
    Yields:
        One row at a time from the user_data table
    """
    try:
        cursor = connection.cursor(dictionary=True)
        offset = 0
        
        while True:
            cursor.execute(
                "SELECT * FROM user_data LIMIT %s OFFSET %s",
                (batch_size, offset)
            )
            rows = cursor.fetchall()
            
            if not rows:
                break
                
            for row in rows:
                yield row
                
            offset += batch_size
            
        cursor.close()
    except mysql.connector.Error as e:
        print(f"Error generating rows: {e}")
        yield None


if __name__ == "__main__":
    # Example usage
    conn = connect_db()
    if conn:
        create_database(conn)
        conn.close()
        
        prodev_conn = connect_to_prodev()
        if prodev_conn:
            create_table(prodev_conn)
            insert_data(prodev_conn, 'user_data.csv')
            
            # Use the generator to stream rows
            for row in row_generator(prodev_conn, 5):
                print(row)
                
            prodev_conn.close()