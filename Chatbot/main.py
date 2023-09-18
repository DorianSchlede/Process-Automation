import openai
import streamlit as st
import os

# Setup OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")
model = "gpt-3.5-turbo"

# Create a list to hold messages
messages = [{'role': 'system', 'content': ""}]

def chat_with_chatgpt(prompt):
    messages.append({'role': 'user', 'content': prompt})
    
    response = openai.ChatCompletion.create(
        model=model,
        temperature=0,
        messages=messages,
    )
    response_content = response["choices"][0]["message"]["content"]
    messages.append({'role': 'assistant', 'content': response_content})
    
    return response_content

# Streamlit UI
st.title('ChatGPT Chatbot')
st.sidebar.header('Settings')
# You can add more settings in the sidebar if needed

user_input = st.text_input("Enter your message...", "")

if st.button("Send") or user_input:
    bot_response = chat_with_chatgpt(user_input)
    user_input = ""  # Clear input field

# Improved chat display
for message in messages:
    if message['role'] == 'user':
        # User's messages on the left
        st.write(f"👤 **You**: {message['content']}")
    else:
        # Bot's messages on the right
        st.write(f"🤖 **AI**: {message['content']}")

st.write("")  # Ensure the latest message is visible (kind of a makeshift auto-scroll)
