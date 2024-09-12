import streamlit as st
import os
import time
from pyairtable import Api
import requests
import json
from anthropic import Anthropic
from pypdf import PdfReader

# Retrieve the API keys from the environment variables
py_airtable_access_key = os.environ['AIRTABLE_ACCESS_KEY']
py_airtable_base_id = os.environ['AIRTABLE_BASE_ID']
py_airtable_table_id = os.environ['AIRTABLE_TABLE_ID'] 

CLAUDE_API_KEY = os.environ["ANTHROPIC_API_KEY"]
anthropic = Anthropic(api_key=CLAUDE_API_KEY)

st.set_page_config(page_title="NuggetStasher", page_icon=":sunglasses:",)
st.write("**NuggetStasher** helps you condense knowledge and store for later")

instruction = st.text_area("Here is my assignment:", "Summarise into a concise para")

uploaded_files = st.file_uploader("Upload your PDF data sources:", type = "pdf", accept_multiple_files = True)
for uploaded_file in uploaded_files:

  raw_text = ""
  if uploaded_file is not None:
    doc_reader = PdfReader(uploaded_file)
    for i, page in enumerate(doc_reader.pages):
      text = page.extract_text()
      if text: raw_text = raw_text + text + "\n"

  with st.spinner("Running AI Model...."):
    start = time.time()
    message = anthropic.messages.create(model = "claude-3-5-sonnet-20240620",
                                        max_tokens = 4096,
                                        temperature = 0,
                                        system = instruction,
                                        messages = [{"role": "user", "content": raw_text}])
    output_text = message.content[0].text
    end = time.time()

  with st.expander("Output"):
    st.write(output_text)
    st.write("Time to generate: " + str(round(end-start,2)) + " seconds")
