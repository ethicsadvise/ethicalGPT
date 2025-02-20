import streamlit as st
import json
import os
import re
import requests
import uuid
import time

DB_DIR = 'user_data'  # Directory to store individual user data
os.makedirs(DB_DIR, exist_ok=True)  # Ensure the directory exists

def stream_data(textto):
    for word in textto.split(" "):
        yield word + " "
        time.sleep(0.02)
        

def get_user_id():
    """Generate or retrieve a unique ID for the user."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())  # Generate a new UUID
    return st.session_state.user_id

def get_user_file(user_id):
    """Return the file path for a user's data file ok."""
    return os.path.join(DB_DIR, f"{user_id}.json")

def load_user_data(user_id):
    """Load chat history for the user."""
    user_file = get_user_file(user_id)
    if os.path.exists(user_file):
        with open(user_file, 'r') as file:
            return json.load(file)
    return {"chat_history": []}  # Default empty chat history

def save_user_data(user_id, data):
    """Save chat history for the user."""
    user_file = get_user_file(user_id)
    with open(user_file, 'w') as file:
        json.dump(data, file)

def main():
    endpoint_url = "https://f32a-34-16-214-26.ngrok-free.app/predict"  # Endpoint URL from .env

    user_id = get_user_id()
    user_data = load_user_data(user_id)

#     st.set_page_config(page_title='Ethical GPT Assistant', layout='wide',
#                 #    initial_sidebar_state=st.session_state.get('sidebar_state', 'collapsed'),
# )

    st.image("./logo/images.jpeg", use_container_width=True )
    
    st.snow()

    intro = """
    ## Welcome to EthicsAdvisor
    
    Ethical GPT is an AI-powered chatbot designed to interact with you in an ethical, safe, and responsible manner. Our goal is to ensure that all responses provided by the assistant are respectful and considerate of various societal and ethical standards.

    Feel free to ask any questions, and rest assured that the assistant will provide helpful and appropriate responses.
    Follow the link below to read about the scenerio that will be used for testing:
    [Scenerio link] (https://docs.google.com/document/d/1G403SC3BPeAxi98sI6uu6BBfMQKw1Tdp2XEpGbleeak/edit?usp=sharing)
    """
    
    st.markdown(intro)

    # Sidebar options
    models = ["llama-ethical"]
    st.sidebar.selectbox("Select Model", models, index=0)

    st.sidebar.title("❄️EthicsAdvisor 📄")
    st.sidebar.caption("Make AI to responde more ethical")
    
   
    with st.sidebar.expander("See fine tuning info"):
        st.caption("Original Data: [Data] (https://huggingface.co/datasets/MasahiroKaneko/eagle/)")
        st.caption("Modified Data: [Data](https://huggingface.co/datasets/ethicsadvisorproject/ethical_data_bigger/) 📝")
        st.caption("Used Model and Notebook: [Original model](https://huggingface.co/ethicsadvisorproject/Llama-2-7b-ethical-chat-finetune/) 🎈, Notebook used for fine tuning [Notebook](https://colab.research.google.com/drive/1eAAjdwwD0i-i9-ehEJYUKXvZoYK0T3ue#scrollTo=ib_We3NLtj2E)")
       
    with st.sidebar.expander("ℹ️ **Take survey**"):
        st.markdown("""You are welcome to give us your input on this research [here](https://forms.office.com/r/H4ARtETV2q).""")
    cols = st.columns(2)

    # Load chat history into session state
    if "messages" not in st.session_state:
        st.session_state.messages = user_data["chat_history"]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Send request to the endpoint
        headers = {'ngrok-skip-browser-warning': 'true'}
        data = {'messages': st.session_state.messages[-1]['content']}

        try:
            response = requests.post(endpoint_url, json=data, headers=headers)
            response.raise_for_status()  # Raise exception for HTTP errors
            response_data = response.json()
            response_text = response_data.get('response_text', '')

            # Clean response text
            message = re.sub(r'<s>\[INST\].*?\[/INST\]', '', response_text).strip()

            with st.chat_message("assistant"):
                st.markdown(message)

            st.session_state.messages.append({"role": "assistant", "content": message})

        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with the endpoint: {e}")
        except KeyError:
            st.error(f"Unexpected response format. Missing 'response_text' key. Received: {response.text}")

        # Save updated chat history
        user_data["chat_history"] = st.session_state.messages
        save_user_data(user_id, user_data)

    # Clear Chat button
    if st.sidebar.button('Clear Chat'):
        st.session_state.messages = []
        user_data["chat_history"] = []
        save_user_data(user_id, user_data)
        st.rerun()

if __name__ == '__main__':
    main()
