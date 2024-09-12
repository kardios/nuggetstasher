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

system_prompt = """You are an advanced AI reading assistant tasked with generating a concise and coherent summary of the given text. Your goal is to identify the main ideas and key details, presenting them in a clear and organized manner, as one single paragraph only.

To complete this task, follow these steps:

1. Carefully read and analyze the entire text.
2. Identify the main topic or central theme of the text.
3. Determine the most important ideas and key supporting details.
4. Prioritize the information, focusing on the most crucial elements.
5. Synthesize the main points into a coherent narrative.

When creating your summary:
- Ensure it captures the essence of the original text.
- Present the information in a logical flow.
- Use clear and concise language.
- Avoid including minor details or examples unless they are crucial to understanding the main points.
- Do not include your own opinions or interpretations; stick to the information provided in the original text.

Remember, your summary must be presented as a single paragraph only, without preambles or headings. Aim for brevity while maintaining clarity and comprehensiveness."""

instruction = st.text_area("Here is my assignment:", system_prompt)

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

  with st.spinner("Stashing away....."):
    airtable_data = {"records": [{"fields": {'Filename': uploaded_file.name, 'Summary': output_text}}]}
    insert_url = f'https://api.airtable.com/v0/{py_airtable_base_id}/{py_airtable_table_id}'
    headers = {'Authorization': f'Bearer {py_airtable_access_key}',
               'Content-Type': 'application/json'}
    insert_response = requests.post(insert_url, json = airtable_data, headers=headers)
  
  with st.expander(uploaded_file.name):
    st.write(output_text)
    st.write("Time to generate: " + str(round(end-start,2)) + " seconds")

  st.snow()
