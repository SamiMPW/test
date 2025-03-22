import streamlit as st
import json
import os
from database import get_connection, create_tables
import bcrypt


def password_strength_check(password):
 
    # https://www.geeksforgeeks.org/python-test-if-string-contains-any-uppercase-character/

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least 1 uppercase character."
    # Add more checks as needed (e.g. uppercase, symbols, etc.)
    return True, ""

def signup():
    st.title("Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Sign Up"):
        if not username:
            st.error("Username cannot be empty.")
            return
        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        valid, msg = password_strength_check(password)
        if not valid:
            st.error(msg)
            return

        try:
            con = get_connection()
            cursor = con.cursor()
            # Check if username already exists.
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            if cursor.fetchone() is not None:
                st.error("Username already exists.")
                return

            # Hash the password
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt)
            # Insert new user with hashed password.
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            con.commit()
            st.success("User created successfully.")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

        finally:
            if con:
                con.close()

def main():
    
    #I need to create the tables before we can run the signup function
    create_tables()
    signup()

if __name__ == "__main__":
    main()