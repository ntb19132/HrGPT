import asyncio
import time

import openai
import streamlit as st
import pinecone
import tiktoken
from streamlit_chat import message

from promp_generator import PromptGenerator
from services.openai import OpenAiApiService


def generate_response(question, chat_logs):
    prompt_gen = PromptGenerator()
    prompt = prompt_gen.retrieve(question)
    prompt = prompt_gen.with_chatlogs(prompt, chat_logs)
    response = OpenAiApiService().get_completion(prompt)
    return response.choices[0].message['content']


# ----------------------- Frontend ---------------------------
# Creating the chatbot interface
async def main():
    st.title("HrGPT : Your HR Assistant")
    st.subheader("Your can ask any information that relate to Sirius")
    # Storing the chat
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if 'input_text' not in st.session_state:
        st.session_state.input_text = 'Hello!'

    def submit():
        st.session_state.input_text = st.session_state.input
        st.session_state.input = ''
        output = generate_response(st.session_state.input_text, st.session_state['history'])
        # store the output
        st.session_state.past.append(st.session_state.input_text)
        st.session_state.generated.append(output)
        st.session_state.history.append({'role': 'user', 'content': f"{st.session_state.input_text}"})
        st.session_state.history.append({'role': 'assistant', 'content': f"{output}"})

    st.text_input(
        "Your Message", '', key="input", on_change=submit)

    if st.session_state['generated']:
        for i, (generated, past) in enumerate(zip(reversed(st.session_state['generated']),
                                                  reversed(st.session_state['past']))):
            message(generated, key=str(i), avatar_style='bottts')
            message(past, is_user=True, key=str(i) + '_user', avatar_style="big-smile")

    message("Hello! How can I assist you today?", key='init_msg', avatar_style='bottts')
    message("Hello!", is_user=True, key='init_msg_user', avatar_style="big-smile")

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
