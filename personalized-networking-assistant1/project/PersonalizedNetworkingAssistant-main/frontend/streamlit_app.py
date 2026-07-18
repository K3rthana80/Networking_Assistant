import streamlit as st

from api import generate_conversation
from components.history import show_history
from components.feedback import feedback_buttons


st.set_page_config(

    page_title="Personalized Networking Assistant",

    page_icon="🤝",

    layout="wide"

)

show_history()

st.title("🤝 Personalized Networking Assistant")

st.write(
    "Generate smart networking conversation starters using AI."
)

event = st.text_area(

    "Event Description"

)

interest = st.text_input(

    "Your Interests"

)

if st.button("Generate Conversation"):

    with st.spinner("Generating..."):

        result = generate_conversation(

            event,

            interest

        )

    st.subheader("🧠 Detected Themes")

    for theme in result["themes"]:

        st.write(

            f"• {theme['theme']} ({theme['confidence']})"

        )

    st.subheader("📖 Wikipedia Summary")

    st.info(

        result["verified_summary"]

    )

    st.subheader("💬 Conversation Starter")

    st.success(

        result["conversation"]

    )

feedback_buttons()