import streamlit as st
from opensearchpy import OpenSearch
import os

# Define the authentication details
host = os.getenv("HOST_OS")
username = os.getenv("USERNAME_OS")
password = os.getenv("PASSWORD_OS")

# Create a connection to your OpenSearch cluster with authentication
client = OpenSearch(
    hosts=[host],
    http_auth=(username, password),
    port=443,  
    use_ssl=True,
)

