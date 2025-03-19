import streamlit as st
import os
import json
from database import get_connection
import bcrypt

def login():
    st.title("Login")

    # Session state initialisation
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    username = st.text_input("Username")
    
    # password needs to be hashed
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        try:
            con = get_connection()
            cursor = con.cursor()
            # Query by username only.
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row and bcrypt.checkpw(password.encode('utf-8'), row[0]):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("Login successful!")
                st.rerun()  # Refresh the page to update state
            else:
                st.error("Invalid username or password")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            if con:
                con.close()

def logout():
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.rerun()

def main():
    if st.session_state.get("logged_in"):
        st.write(f"Logged in as: {st.session_state.get('username')}")
        logout()
    else:
        login()

if __name__ == "__main__":
    main()