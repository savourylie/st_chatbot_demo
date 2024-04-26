import streamlit as st
import requests
import json
from pypdf import PdfReader
from io import BytesIO

# Define the API endpoint URL
URL = 'http://localhost:11434/api/generate'

# App title
st.set_page_config(page_title="🤗💬 LLM Chatbot")
    
# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function for generating LLM response
def generate_response(prompt_input):
    # Create the data payload as a dictionary
    payload = {
                "model": "llama3:instruct",
                "prompt": prompt_input,
                "stream": False
              }

    response = requests.post(URL, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        return data["response"]
    else:
        return "Failed to get a response from the server, status code:", response.status_code

def messages2string(messages):
    text = ""

    for m in messages:
        text += f"{m['role']}: {m['content']}\n"

    return text + "assistant: "

# File uploader
uploaded_file = st.file_uploader("Upload your PDF file", type=['pdf'])
if uploaded_file is not None:
    with st.spinner('Processing PDF...'):
        # Read PDF file
        file_reader = PdfReader(BytesIO(uploaded_file.getvalue()))
        total_pages = len(file_reader.pages)
        pdf_text = ''
        for page in range(total_pages):
            pdf_text += file_reader.pages[page].extract_text()
        st.session_state.messages.append({"role": "assistant", "content": f"Received PDF with {total_pages} pages. Processing content..."})
        # Optional: process or display PDF text
        st.text_area("PDF Text", value=pdf_text, height=300)


# User-provided prompt
if prompt := st.chat_input(disabled=False):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(messages2string(st.session_state.messages)) 
            # print(response)
            st.write(response) 
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)