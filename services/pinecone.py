import os
import streamlit as st
import pinecone

pinecone.init(
    api_key=st.secrets["pinecone_key"],
    environment="asia-southeast1-gcp"  # find next to api key in console
)

index = pinecone.Index('hrgpt')


def search(embedded):
    response = index.query(embedded, top_k=10, include_metadata=True)
    contexts = [
        x['metadata'] for x in response['matches']
    ]
    return contexts
