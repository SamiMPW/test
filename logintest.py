import streamlit as st

# databases: usernames, pws
# database: previous journeys
# database: station names, lines, times to travel between them

# feedback page that sends email to developers
# password strength check

# def signup():
# button to go to signup page
# database basic encryption


# Placeholder users for login
USER_CREDENTIALS = {
    "admin": "password123",
    "user1": "securepass",
}
# Function to display the signup page
def signup():
    st.title("TFL Journey Planner - Signup")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    signup_button = st.button("Signup")
    
    if signup_button:
        if username in USER_CREDENTIALS:
            st.error("User already exists")
        else:
            USER_CREDENTIALS[username] = password
            st.success("Registration Complete.")
            
# Function to display the login page
def login():
    st.title("TFL Journey Planner - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("Login successful!")
        else:
            st.error("Invalid username or password")

# Function to display the journey planner
def journey_planner():
    st.title("TFL Journey Planner")
    st.write(f"Welcome, {st.session_state.get('username', 'User')}!")

    # Input fields for "From" and "To" locations
    from_location = st.text_input("From")
    to_location = st.text_input("To")

    # Placeholder for journey planning
    if st.button("Plan Your Journey"):
        if from_location and to_location:
            # Placeholder for journey planning logic
            st.info("Journey planning logic is under development.")
            st.write(f"From: {from_location}")
            st.write(f"To: {to_location}")
            st.write("Estimated time: -- (to be implemented)")
        else:
            st.error("Please provide both 'From' and 'To' locations.")

# Main application logic
def main():
    st.sidebar.title("TFL Journey Planner")
    st.sidebar.button("Home")
    st.sidebar.button("Feedback")
    # Initialize session state variables
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # Display login page or journey planner based on login status
    if st.session_state["logged_in"]:
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.experimental_rerun()
        journey_planner()
    else:
        login()

if __name__ == "__main__":
    main()
