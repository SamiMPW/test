import streamlit as st
from database import get_connection

def feedback():
    st.title("Feedback")
    st.write("Please share your thoughts or bugs you've encountered.")

    feedback_text = st.text_area("Your feedback here")
    star_rating = st.slider("Rate your experience (1-5 stars)", min_value=1, max_value=5, value=3)
    submit_button = st.button("Submit")

    if submit_button:
        if feedback_text.strip():
            try:
                # Adding user feedback to database 
                # Following lines are for connecting to the database and inserting the feedback
                con = get_connection()
                cursor = con.cursor()
                 # Assuming the user is logged in and their username is stored in session state
                username = st.session_state.get("username", "Anonymous user")

                # Get the user id from username
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                # fetchone: Fetch the next row of a query result
                # Insert feedback into the feedback table
                cursor.execute(
                    "INSERT INTO feedback (user_id, feedback_text, rating) VALUES (?, ?, ?)",
                    (username, feedback_text, star_rating))
                con.commit()

                st.success("Thank you for your feedback!")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                if con:
                    con.close()
        else:
            st.error("Feedback cannot be empty.")
            

def main():
    feedback()

if __name__ == "__main__":
    main()