import streamlit as st

from api import get_history


def show_history():

    st.sidebar.header("📚 Recent Conversations")

    history = get_history()

    history = history[::-1][:5]

    for item in history:

        st.sidebar.write(
            f"**{item['event']}**"
        )

        st.sidebar.caption(
            item["conversation"]
        )