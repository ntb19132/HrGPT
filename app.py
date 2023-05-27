import asyncio
import time

import streamlit as st
from streamlit_chat import message

from promp_generator import PromptGenerator, count_tokens
from services.obs import write_log
from services.openai import get_completion
from utils import get_session_id


async def generate_response(question, chat_logs):
    user_timestamp = int(time.time())
    prompt_gen = PromptGenerator()
    docs = prompt_gen.retrieve(question)
    prompt = prompt_gen.get_prompt(question, docs, chat_logs)
    response = get_completion(prompt)
    generated_content = response.choices[0].message['content']
    # write session_id, created, role , content, docs
    session_id = get_session_id()
    # session_id = 'asda'
    usage = response.usage.to_dict()
    usage['embedding_token'] = count_tokens(question)
    doc_ids = [d['id'] for d in docs]
    user_log = {'session_id': session_id, 'timestamp': user_timestamp, 'role': 'user', 'content': question,
                'docs': doc_ids, 'usage': usage}
    write_log(user_log, len(chat_logs))
    assistant_log = {'session_id': session_id, 'timestamp': response['created'], 'role': 'assistant', 'content': generated_content}
    write_log(assistant_log, len(chat_logs)+1)
    st.session_state.past.append(st.session_state.input_text)
    st.session_state.generated.append(generated_content)
    st.session_state.chatlogs.append({'role': 'user', 'content': f"{st.session_state.input_text}"})
    st.session_state.chatlogs.append({'role': 'assistant', 'content': f"{generated_content}"})
    # return generated_content


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
        asyncio.run(generate_response(st.session_state.input_text, st.session_state['chatlogs']))
        # store the output

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
    main()
