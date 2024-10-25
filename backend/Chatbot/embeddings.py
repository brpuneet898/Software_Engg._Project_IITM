import os
import numpy as np
import pandas as pd
import google.generativeai as genai
API_KEY= "AIzaSyAptDqXJLYJTf2ttp_8J1ZN3em9P2HkfSg"
genai.configure(api_key=API_KEY)
from langchain.text_splitter import RecursiveCharacterTextSplitter

def read_txt_files(directory, chunk_size=5000, chunk_overlap=120):
    documents = []
    filenames = os.listdir(directory)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    for filename in filenames:
        if filename.endswith('.txt'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                chunks = text_splitter.split_text(content)
                for chunk in chunks:
                    documents.append({
                        "Title": filename.replace('.txt', ''),
                        "Content": chunk
                    })
    return documents

# Specify the directory containing your TXT files
txt_directory = './Retrieval_docs'
documents = read_txt_files(txt_directory)
df = pd.DataFrame(documents)
df.columns = ['Title', 'Content']

# Get the embeddings of each text and add to an embeddings column in the dataframe
model = 'models/text-embedding-004'

def embed_fn(title, text):
  return genai.embed_content(model=model,
                             content=text,
                             task_type="retrieval_document",
                             title=title)["embedding"]

df['Embeddings'] = df.apply(lambda row: embed_fn(row['Title'], row['Content']), axis=1)

# Save the dataframe in structured format
df.to_pickle('dataframe.pkl')
