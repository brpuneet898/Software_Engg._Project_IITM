from flask import render_template,request,redirect,url_for,Blueprint,flash,abort,jsonify, Flask
from flask_restful import Resource, Api
from backend.GA.llm_setup import *
from backend.GA.lecture_database import *
from backend.Chatbot.chatbot import chat_bot
# TODO
chatt = Blueprint("chatbot",__name__,static_folder = '../static',template_folder="../templates" )


@chatt.route('/api/chatbot_page', methods=['POST'])
def chatbot_page():

    """
    ---
    post:
      summary: Chatbot for general questions
      description: Route for chatbot page
      responses:
        200:
          description: Success
    """       
    data = request.get_json()
    user_message = data.get('message', '')
    print(user_message)
    chatbot_response = chat_bot(str(user_message))
    # sample repsonse, modify this Aryan to send the actual chatbot thing

    return jsonify({'response': chatbot_response})

# TODO
@chatt.route('/api/chat/clear')
def clearchat():

    """
    ---
    delete:
      summary: Clear Chat History
      description: Clears all chat history involving the chatbot and current user
      responses:
        200:
          description: Success
    """       
    return jsonify({"message":"chat cleared"}),200


#  TODO
@chatt.route('/api/chat_chain', methods=['POST'])
def chat_chain():

    """
    ---
    post:
      summary: Chain LLM conversation
      description: Endpoint to chain LLM conversations and generate responses.
      responses:
        200:
          description: Success
    """    
    data = request.get_json()
    conversation_chain = data.get('messages', [])
    return jsonify({"role": "assistant", "content": "Yes,it will rain."}),200