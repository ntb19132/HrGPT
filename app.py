import openai
import streamlit as st
import pinecone
from streamlit_chat import message

# ----------------------- Import Secret Key -------------------------
openai.api_key = st.secrets["api_secret"]
pinecone_key = st.secrets["pinecone_key"]

# ------------------------ Configuration ----------------------------
MODEL = "text-embedding-ada-002"
EMBEDDING_CTX_LENGTH = 1536

# ----------------------- Connect to Pinecone ---------------------------
index_name = 'hrgpt'

# initialize connection to pinecone (get API key at app.pinecone.io)
pinecone.init(
    api_key=pinecone_key,
    environment="asia-southeast1-gcp"  # find next to api key in console
)

# check if index already exists (it shouldn't if this is first time)
if index_name not in pinecone.list_indexes():
    st.error("Can't Connect to Pinecone")
# connect to index
index = pinecone.Index(index_name)

# ------------------------ Query Engine ---------------------------


def retrieve(query, limit=4000):
    # Create embeddings for the query
    res = openai.Embedding.create(
        input=[query],
        engine=MODEL
    )

    # Retrieve from Pinecone
    xq = res['data'][0]['embedding']

    # Get relevant contexts
    res = index.query(xq, top_k=3, include_metadata=True)
    contexts = [
        x['metadata']['text'] for x in res['matches']
    ]
    # Build the initial part of our prompt with the retrieved contexts included
    prompt_start = f"""Answer the question based on the context below. If the answer cannot be found, write "I don't know."\n\nContext:\n"""

    # Define the end of the prompt
    prompt_end = (
        f"\n\nQuestion: {query}\nAnswer:"
    )
    # Append contexts until hitting the limit
    for i in range(1, len(contexts)):
        # If adding another context exceeds the limit, break and use the current set of contexts
        if len("\n\n---\n\n".join(contexts[:i])) >= limit:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts[:limit]) +
                prompt_end
            )
            break
        # If this is the last context and it doesn't exceed the limit, add it to the prompt
        elif i == len(contexts)-1:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts) +
                prompt_end
            )
    # Return the final prompt
    return prompt

# ----------------------- Chat engine ---------------------------


def get_completion(prompt, log_length=5, model="gpt-3.5-turbo", max_tokens=100):
    # If the length of the context exceeds the log_length, take only the last log_length elements
    history = st.session_state['history']
    if len(history) > log_length:
        chatlog = history[-log_length:]
    # If not, take the whole context
    else:
        chatlog = history
    # Prepare the messages to be sent to the model, including system message, context and user's prompt
    messages = [{'role': 'system', 'content': 'You are an HR assistant that answers questions to the employee.'}
                ] + chatlog + [{"role": "user", "content": prompt}]
    # Make the API call to generate a response
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
        max_tokens=max_tokens
    )
    # Return the content of the model's response
    return response.choices[0].message["content"]


def generate_response(question):
    prompt = retrieve(question)
    message = get_completion(prompt)
    return message


# ----------------------- Frontend ---------------------------
# Creating the chatbot interface
st.title("HrGPT : Your HR Assistant")
st.subheader("Your can ask any information that relate to Sirius")

# Storing the chat
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'history' not in st.session_state:
    st.session_state['history'] = []
    # We will get the user's input by calling the get_text function


def submit():
    st.session_state.widget = ''


if 'input_text' not in st.session_state:
    st.session_state.input_text = 'Hello!'


def submit():
    st.session_state.input_text = st.session_state.input
    st.session_state.input = ''


def get_text():
    input_text = st.text_input(
        "Your Message", '', key="input", on_change=submit)

    return st.session_state.input_text


user_input = get_text()

if user_input:
    output = generate_response(user_input)  # Add generate text function here
    # store the output
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)
    st.session_state.history.append(
        {'role': 'user', 'content': f"{user_input}"})
    st.session_state.history.append({'role': 'user', 'content': f"{output}"})

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i],
                key=str(i), avatar_style='bottts')
        message(st.session_state['past'][i],
                is_user=True, key=str(i) + '_user', avatar_style="big-smile")
