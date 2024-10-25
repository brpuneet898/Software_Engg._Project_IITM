import textwrap
import numpy as np
import pandas as pd
import google.generativeai as genai
from IPython.display import Markdown
import os 

# Suppress logging warnings
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
API_KEY = "AIzaSyAptDqXJLYJTf2ttp_8J1ZN3em9P2HkfSg"

genai.configure(api_key=API_KEY)
#path = "backend\Chatbot\dataframe.pkl"
current_dir = os.path.dirname(__file__) 
path = os.path.join(current_dir, 'dataframe.pkl')
df = pd.read_pickle(path)
model = 'models/text-embedding-004'


def find_best_passage(query, dataframe):
  query_embedding = genai.embed_content(model=model,
                                        content=query,
                                        task_type="question_answering")
  dot_products = np.dot(np.stack(dataframe['Embeddings']), query_embedding["embedding"])
  idx = np.argmax(dot_products)
  return dataframe.iloc[idx]['Content'] # Return text from index with max value

def make_prompt(query, relevant_passage):
  escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
  prompt = textwrap.dedent("""You are a helpful and informative bot that answers questions using text from the reference passage included below and the internet. \
  Be sure to respond in a complete and to the point sentence (answer must be of atleast 50 words), being comprehensive, including all relevant background information. \
  If the passage is irrelevant to the answer, you may ignore it.if someone says hi ,please greet them and if they ask question unrelated to software engineering, please reply "i can't answer that". \
  Note : Instead of Bullet points use numbers and remove symbols like "*" from response i.e. make response HTML Friendly\ 
  QUESTION: '{query}'
  PASSAGE: '{relevant_passage}'

    ANSWER:
  """).format(query=query, relevant_passage=escaped)

  return prompt

def chat_bot(query: str):
  passage = find_best_passage(query, df)
  prompt = make_prompt(query, passage)
  model = genai.GenerativeModel('gemini-1.5-pro-latest')
  answer = model.generate_content(prompt)
  return Markdown(answer.text).data

'''
passage = find_best_passage(query, df)
prompt = make_prompt(query, passage)
model = genai.GenerativeModel('gemini-1.5-pro-latest')
answer = model.generate_content(prompt)
print(answer.text)'''