import streamlit as st
import json
import os
from database import get_connection, create_tables



def password_strength_check(password):
    """
    A very basic password strength check.
    Extend with more rules as needed.
    """
    # https://www.geeksforgeeks.org/python-test-if-string-contains-any-uppercase-character/

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least 1 uppercase character."
    # Add more checks as needed (e.g. uppercase, symbols, etc.)
    return True, ""

def signup():
    st.title("Sign Up")

    username = st.text_input("Choose a username")
    password = st.text_input("Choose a password", type="password")
    confirm_password = st.text_input("Confirm password", type="password")
    signup_button = st.button("Sign Up")

    if signup_button:
        if not username or not password or not confirm_password:
            st.error("All fields are required.")
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
            
            # cursor's job is to collect database queries etc
            cursor = con.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            
            # fetchone: Fetch the next row of a query result
            # basically if name already exists, then the username is taken
            if cursor.fetchone() is not None:
                st.error("Username already exists.")
                return
            
            # insert new user
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            
            # commit the changes
            con.commit()
            
            # success message
            st.success("User created successfully.")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        
        # last step if we are able to run the code above, we close the connection to the db
        finally:
            if con:
                con.close()

def main():
    
    # we need to create the tables before we can run the signup function
    create_tables()
    signup()

if __name__ == "__main__":
    main()