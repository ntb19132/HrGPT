import asyncio
import time

import requests
import streamlit as st
from components.streamlit_chat import message

from promp_generator import PromptGenerator, count_tokens
from services.obs import write_log
from services.openai import get_completion
from utils import get_session_id

RELEASE = st.secrets.get("RELEASE", True)

if RELEASE:
    demo_endpoints = {"hrgpt": "https://hrgpt-api.onrender.com/chat/completions",
                      "marketgpt": "https://stockmarketgpt-api.onrender.com/chat/completions"}
else:
    demo_endpoints = {"hrgpt": "http://127.0.0.1:8000/chat/completions",
                      "marketgpt": "http://127.0.0.1:7000/chat/completions"}


async def generate_response(demo, chat_logs):
    usage = None
    if demo == 'hrgpt':
        payload = {"messages": chat_logs}
        response = requests.post(demo_endpoints[demo], json=payload)
        data = response.json()
        generated_content = data['message']['content']
        created = data['created']
        usage = data['usage']
    else:
        payload = {"content": chat_logs[-1]['content']}
        response = requests.post(demo_endpoints[demo], json=payload)
        data = response.json()
        generated_content = data['message']['content']
        created = data['created']
        usage = data['usage']
    # write session_id, created, role , content, docs
    session_id = get_session_id()
    # session_id = 'asd'
    assistant_log = {'session_id': session_id, 'timestamp': created, 'role': 'assistant',
                     'content': generated_content, 'usage': usage, 'feed_back': None, 'app': demo}
    # print(assistant_log)
    if RELEASE:
        write_log(assistant_log, len(chat_logs) + 1)
    st.session_state.chatlogs.append(assistant_log)


# ----------------------- Frontend ---------------------------
# Creating the chatbot interface
def main():
    st.title("HrGPT : Your HR Assistant")
    st.subheader("Your can ask any information that relate to Sirius")
    # Storing the chat
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    if 'chatlogs' not in st.session_state:
        st.session_state['chatlogs'] = []

    if 'input_text' not in st.session_state:
        st.session_state.input_text = 'Hello!'

    def submit():
        st.session_state.input_text = st.session_state.input
        st.session_state.input = ''
        user_log = {'session_id': get_session_id(), 'timestamp': int(time.time()), 'role': 'user',
                    'content': st.session_state.input_text, 'app': st.session_state.demo}
        st.session_state.chatlogs.append(user_log)
        chat_logs = [{'role': log['role'], 'content': log['content']} for log in st.session_state['chatlogs']]
        asyncio.run(generate_response(st.session_state.demo, chat_logs))
        write_log(user_log, len(chat_logs))
        # store the output

    col1, col2 = st.columns([1, 3])
    st.session_state.demo = col1.selectbox(
        "pick demo",
        ('hrgpt', 'marketgpt'))

    col2.text_input(
        "Your Message", '', key="input", on_change=submit)

    if st.session_state['chatlogs']:
        for i, log in reversed(list(enumerate(st.session_state['chatlogs']))):
            is_user = (log['role'] == 'user')
            avatar = 'big-smile' if is_user else 'bottts'
            feed_back = message(log['content'], is_user=is_user, key=str(i), avatar_style=avatar)
            if not is_user and feed_back != log['feed_back']:
                log['feed_back'] = feed_back
                write_log(log, i)

    message("Hello! How can I assist you today?", key='init_msg', avatar_style='bottts')
    message("Hello!", is_user=True, key='init_msg_user', avatar_style="big-smile")


if __name__ == "__main__":
    main()
