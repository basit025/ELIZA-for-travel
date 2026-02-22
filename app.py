import streamlit as st
import time

# Import the respond function from our existing chatbot script
from travel_chatbot import respond

# Set up the page configuration
st.set_page_config(
    page_title="Travel & Hotel Booking Assistant",
    page_icon="✈️",
    layout="centered"
)

# Customizing the UI completely
st.title("✈️ Travel & Hotel Booking Assistant 🏨")
st.markdown("""
Welcome to your personal Travel Booking Assistant! 
You can use this chatbot to book **Flights** and **Hotels**.

### 💡 Tips to get started:
* **Flights:** "Book a flight from London to Paris", specify "Economy" or "Business", and the number of tickets.
* **Hotels:** "Find a hotel in Lahore", specify "Luxury" or "Budget", pick a hotel, and state the number of rooms.
""")
st.divider()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add initial bot greeting
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello! I am your Travel Booking Assistant. Do you want to book a flight or a hotel today?"
    })

# Display chat history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if user_input := st.chat_input("Type your message here..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get Bot response using the imported `respond` function
    reply = respond(user_input)
    
    # Display assistant response in chat message container with a slight delay for realism
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        # Simulated typing effect
        full_response = ""
        for chunk in reply.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": reply})
