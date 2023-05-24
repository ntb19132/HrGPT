import os
import streamlit as st
import pinecone

pinecone.init(
    api_key=st.secrets["pinecone_key"],
    environment="asia-southeast1-gcp"  # find next to api key in console
)


class PineconeService:
    def __init__(self):
        self.index = pinecone.Index('hrgpt')

    def search(self, embedded):
        response = self.index.query(embedded, top_k=10, include_metadata=True)
        contexts = [
            x['metadata']['text'] for x in response['matches']
        ]
        return contexts
