import streamlit as st
import os
import json

# Utility functions to read/write user data
def read_users_data():
    if not os.path.exists("users_data.json"):
        return {}
    with open("users_data.json", "r") as file:
        return json.load(file)

def login():
    st.title("Login")

    # Session state initialisation
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        users = read_users_data()
        # Verify username and password
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("Login successful!")
            st.experimental_rerun()  # Refresh the page to update state
        else:
            st.error("Invalid username or password")

def logout():
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.experimental_rerun()

def main():
    if st.session_state.get("logged_in"):
        st.write(f"Logged in as: {st.session_state.get('username')}")
        logout()
    else:
        login()

if __name__ == "__main__":
    main()