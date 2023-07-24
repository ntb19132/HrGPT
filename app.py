import asyncio
import time

import requests
import streamlit as st
from components.streamlit_chat import message

from promp_generator import PromptGenerator, count_tokens
from services.obs import write_log
from services.openai import get_completion
from utils import get_session_id
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
RELEASE = st.secrets.get("RELEASE", True)

if RELEASE:
    demo_endpoints = {"hrgpt-api": "https://hrgpt-api.onrender.com/chat/completions",
                      "external-marketgpt-api": "https://marketgpt-api-v1.onrender.com/chat/completions",
                      # "marketgpt-api": "https://stockmarketgpt-api.onrender.com/chat/completions",
                      "internal-marketgpt-api": "https://pi-marketgpt-api.onrender.com/chat/completions"}
else:
    demo_endpoints = {"hrgpt-api": "http://127.0.0.1:8000/chat/completions",
                      "external-marketgpt-api": "http://127.0.0.1:7000/chat/completions",
                      "internal-marketgpt-api": "http://127.0.0.1:8000/chat/completions"}


async def generate_response(demo, chat_logs):
    usage = None
    generated_visualization = None
    if demo == 'hrgpt':
        question = chat_logs[-1]['content']
        prompt_gen = PromptGenerator()
        docs = prompt_gen.retrieve(question)
        prompt = prompt_gen.get_prompt(question, docs, chat_logs[:-1])
        response = get_completion(prompt)
        generated_content = response.choices[0].message['content']
        usage = response.usage.to_dict()
        usage['embedding_token'] = count_tokens(question)
        created = response.created
        # doc_ids = [d['id'] for d in docs]
    elif demo == 'hrgpt-api':
        payload = {"messages": chat_logs}
        response = requests.post(demo_endpoints[demo], json=payload)
        data = response.json()
        generated_content = data['message']['content']
        created = data['created']
        usage = data['usage']
    elif demo == 'internal-marketgpt-api' or demo == 'external-marketgpt-api':
        payload = {"content": chat_logs[-1]['content']}
        response = requests.post(demo_endpoints[demo], json=payload)
        data = response.json()
        print(data)
        generated_content = data['message']['content']
        generated_visualization = data.get('visualization', None)
        created = data['created']
        usage = {}
    # write session_id, created, role , content, docs
    session_id = get_session_id()
    # session_id = 'asd'
    assistant_log = {'session_id': session_id, 'timestamp': created, 'role': 'assistant',
                     'content': generated_content, 'visualization': generated_visualization,
                     'usage': usage, 'feed_back': None, 'app': demo}
    # print(assistant_log)
    if RELEASE:
        write_log(assistant_log, len(chat_logs) + 1)
    st.session_state.chatlogs.append(assistant_log)


# ----------------------- Frontend ---------------------------
# Creating the chatbot interface
def main():
    st.title("Chatbot demo")
    st.subheader("Your can ask any information that relate to the demo")
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
        ('external-marketgpt-api', 'hrgpt', 'hrgpt-api', 'internal-marketgpt-api'))

    col2.text_input(
        "Your Message", '', key="input", on_change=submit)

    if st.session_state['chatlogs']:
        for i, log in reversed(list(enumerate(st.session_state['chatlogs']))):
            is_user = (log['role'] == 'user')
            avatar = 'big-smile' if is_user else 'bottts'
            feed_back = message(log['content'], is_user=is_user, key=str(i), avatar_style=avatar)
            if not is_user and log['visualization'] is not None:
                if log['visualization']['type'] == 'candlestick':
                    data = log['visualization']['data']
                    name = log['visualization']['name']
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                        vertical_spacing=0.03, subplot_titles=(name, 'Volume'),
                                        row_width=[0.2, 0.7])

                    # Plot OHLC on 1st row
                    fig.add_trace(go.Candlestick(x=pd.to_datetime(data['x'], unit='s'),
                                                 open=data['y'][0],
                                                 high=data['y'][1],
                                                 low=data['y'][2],
                                                 close=data['y'][3],
                                                 name=name),
                                  row=1, col=1
                                  )
                    # indicators
                    for indicator, values in zip(data['yaxis'][6:], data['y'][6:]):
                        fig.add_trace(go.Scatter(x=pd.to_datetime(data['x'], unit='s'), y=values, mode='lines', name=indicator)
                                      , row=1, col=1)
                    # Bar trace for volumes on 2nd row without legend
                    fig.add_trace(go.Bar(x=pd.to_datetime(data['x'], unit='s'), y=data['y'][4], showlegend=False), row=2, col=1)
                    fig.update(layout_xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, theme="streamlit")
                else:
                    st.json(log['visualization'], expanded=False)
            if not is_user and feed_back != log['feed_back']:
                log['feed_back'] = feed_back
                write_log(log, i)

    message("Hello! How can I assist you today?", key='init_msg', avatar_style='bottts')
    message("Hello!", is_user=True, key='init_msg_user', avatar_style="big-smile")


if __name__ == "__main__":
    main()
