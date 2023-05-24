import logging
import os
import time
import streamlit as st
import openai

openai.api_key = st.secrets["api_secret"]
OPENAI_MODEL = "gpt-3.5-turbo"
EMBED_MODEL = 'text-embedding-ada-002'
logger = logging.getLogger(__name__)


class OpenAiApiService:
    def __init__(self):
        ...

    def get_completion(self, msgs):
        # Make your API call
        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=msgs,
                temperature=0
            )  # Replace with the actual API call you want to make
            return response
        except openai.error.RateLimitError:
            # If RateLimitError is encountered, retry after a delay
            logger.warning("RateLimitError encountered. Retrying in 10 seconds...")
            time.sleep(10)
            return self.get_completion(msgs)

    def get_embedded(self, query):
        response = openai.Embedding.create(
            input=[query],
            engine=EMBED_MODEL
        )
        return response
