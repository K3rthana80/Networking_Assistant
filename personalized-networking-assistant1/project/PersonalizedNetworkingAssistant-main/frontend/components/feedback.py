import streamlit as st

from api import send_feedback


def feedback_buttons():

    col1, col2 = st.columns(2)

    with col1:

        if st.button("👍 Helpful"):

            send_feedback("Helpful")

            st.success("Thanks!")

    with col2:

        if st.button("👎 Improve"):

            send_feedback("Needs Improvement")

            st.info("Feedback recorded.")