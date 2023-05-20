import openai
import streamlit as st

# pip install streamlit-chat
from streamlit_chat import message

openai.api_key = st.secrets["api_secret"]


def generate_response(prompt):
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message = completions.choices[0].text
    return message


# Creating the chatbot interface
st.title("chatBot : Streamlit + openAI")

# Storing the chat
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

    # We will get the user's input by calling the get_text function


def submit():
    st.session_state.widget = ''


if 'input_text' not in st.session_state:
    st.session_state.input_text = 'Hello?'


def submit():
    st.session_state.input_text = st.session_state.input
    st.session_state.input = ''


def get_text():
    input_text = st.text_input(
        "Your Message", '', key="input", on_change=submit)

    return st.session_state.input_text


user_input = get_text()

if user_input:
    output = generate_response(user_input)
    # store the output
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i],
                key=str(i), avatar_style='shapes')
        message(st.session_state['past'][i],
                is_user=True, key=str(i) + '_user')
