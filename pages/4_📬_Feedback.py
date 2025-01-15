import streamlit as st

def feedback():
    st.title("Feedback")
    st.write("Please share your thoughts or bugs you've encountered.")

    feedback_text = st.text_area("Your feedback here")
    submit_button = st.button("Submit")

    if submit_button:
        if feedback_text.strip():
            # In real app, send the feedback via email or store in DB
            st.success("Thank you for your feedback!")
        else:
            st.error("Feedback cannot be empty.")

def main():
    feedback()

if __name__ == "__main__":
    main()