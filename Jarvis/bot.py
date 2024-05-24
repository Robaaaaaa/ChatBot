import streamlit as st
import replicate
import os

st.title("Jarvis ChatBot")

api_key = None


# Check if the API key is provided via Streamlit secrets
if 'REPLICATE_API_TOKEN' in st.secrets:
    api_key = st.secrets['REPLICATE_API_TOKEN']
else:
    # If not, allow the user to input the API key manually
    with st.sidebar:
        api_key = st.text_input('Enter Replicate API token:', type='password')

        # Basic validation for the API key
        if api_key:
            if not (api_key.startswith('r8_') and len(api_key) == 40):
                st.error('Please enter a valid API token!')
            else:
                st.success('Proceed to entering your prompt message!', icon='👉🏿')

# Set the API key as an environment variable if it is provided
if api_key:
    os.environ['REPLICATE_API_TOKEN'] = api_key

# Store generated responses
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "What do you wish to know about?"}]

# Display/Clear chat messages
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        st.text_input("Your message:", value=message["content"], disabled=True, key=f"user_message_{i}")
    elif message["role"] == "assistant":
        st.write(message["content"], key=f"assistant_message_{i}")

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "What do you wish to know about ?"}]
    st.experimental_rerun()

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function to generate responses
def generate_response():
    dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond as Assistant\n\n"
    
    for msg in st.session_state.messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        dialogue += f"{role}: {msg['content']}\n\n"

    # Use Replicate API to generate the response
    output = replicate.run(
        'meta/llama-2-7b-chat',
        input={
            "prompt": f"{dialogue} Assistant:",
            "temperature": 0.7,  # Adjusted for more varied responses
            "top_p": 0.85,  # Adjusted for more focused sampling
            "max_length": 200,  # Adjusted length
            "repetition_penalty": 1.2  # Penalizing repetition
        }
    )

    return output

# User prompt
if prompt := st.chat_input(disabled=not api_key):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate new response if the last message was from the user
    with st.chat_message("assistant"):
        with st.spinner("Preparing your answer..."):
            response = generate_response()
            full_response = ''.join(response)
            st.write(full_response)

            st.session_state.messages.append({"role": "assistant", "content": full_response})
