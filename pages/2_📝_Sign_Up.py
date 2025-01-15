import streamlit as st
import json
import os

def read_users_data():
    if not os.path.exists("users_data.json"):
        return {}
    with open("users_data.json", "r") as file:
        return json.load(file)

def write_users_data(data):
    with open("users_data.json", "w") as file:
        json.dump(data, file, indent=4)

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

        users = read_users_data()

        if username in users:
            st.error("Username already taken. Please choose another one.")
        else:
            # Create user
            users[username] = password
            write_users_data(users)
            st.success("Sign-up successful! You can now log in.")

def main():
    signup()

if __name__ == "__main__":
    main()