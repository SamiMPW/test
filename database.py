import sqlite3
import os

# https://docs.python.org/3/library/sqlite3.html
# >sql


db_name="app_database.db"
# Connection function
# Create tables function
# Add user function
# Get user function
# Add feedback 
# Get feedback
# Get user by ID


def get_connection():
    # establish the connection with the db
    con = sqlite3.connect(db_name)
    return con

def create_tables():

    # using the function from earlier to establish the connection
    con = get_connection()

    # intialise cursor, cursor lets us interact with the sql db
    cursor = con.cursor()

    # create users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username STRING NOT NULL UNIQUE,
            password STRING NOT NULL
        );
        """
    )
    
    # create feedback table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            feedback_text STRING NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )

    # commit the creation tables
    con.commit()

    # close the connection
    con.close()
    
    

    
    