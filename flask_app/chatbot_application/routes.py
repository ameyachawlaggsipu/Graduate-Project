from flask import render_template, request, jsonify, session, redirect, url_for, abort

from chatbot_application import app
import os
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from tqdm import tqdm
from langchain_openai import OpenAIEmbeddings
from chatbot_application.utils import *

from chatbot_application.message_encoder import MessageEncoder

EMBEDDINGS_DIR = "chatbot_application/document_embeddings"
default_system_message = SystemMessage("You are a mental health therapist. Start every message with 'Huzzah!!!'.")
mapping = generate_mapping("chatbot_application/static/Mapping.csv")
mapping_screening_tool = generate_screening_tool_mapping("chatbot_application/static/Mapping_Screening_Tool.csv")
#default_system_message = None

def get_vector_db():
    return Chroma(persist_directory=EMBEDDINGS_DIR, embedding_function=OpenAIEmbeddings())


@app.route("/")
@app.route("/home")
def home():
    session["conversation_history"] = []
    session["recommended_resources"] = []
    if not os.path.isdir(EMBEDDINGS_DIR):
        abort(500, "Embeddings need to be placed in the proper directory - "+
                                "chatbot_application/document_embeddings.")
        #raise FileNotFoundError("Embeddings need to be placed in the proper directory - \\"
         #                       "chatbot_application/document_embeddings.")
    if "OPENAI_API_KEY" not in os.environ:
        abort(500, "OPENAI_API_KEY needs to be defined in the system environment variables.")
        #raise EnvironmentError("OPENAI_API_KEY needs to be defined in the system environment variables.")

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template("chatbot.html", title="Mental Health Chat")

@app.errorhandler(500)
def internal_error(e):
    return render_template('error500_page.html', reason=e.description)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hardcoded single user credentials
        if username == 'demo_user' and password == '1234':
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return 'Login Failed'
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


def get_chatbot_response(message):
    vector_db = get_vector_db()
    pdf_qa = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(temperature=0.5, model_name='gpt-3.5-turbo'),
        retriever=vector_db.as_retriever(search_kwargs={'k': 30}),
        return_source_documents=True,
        verbose=False
    )

    query = message
    conversation_history = session["conversation_history"]
    conversation_history = [MessageEncoder.from_dict(message) for message in conversation_history]
   
    result = pdf_qa.invoke(
        {"question": query, "chat_history":  conversation_history}
    )
    source = get_first_source_doc_title(result)
    source_link = mapping[source]

    conversation_history.extend((HumanMessage(content=query), AIMessage(result['answer'])))
    session["conversation_history"] = [MessageEncoder(message).to_dict() for message in conversation_history]

    response = result['answer']

    if len(response.split()) > 50 and has_confident_source(result) and source_link not in session["recommended_resources"]:
        # For basic sentences, no source, but long responses (>50 words), return a source
        # Only return source if not given to the user before, so that the same source is not repeatedly recommended.
        response += "<br><br>For more details, refer to: <a href='" + source_link + "' target='_blank'>"+get_first_source_webpage_title(result)+"</a>"
        session["recommended_resources"].append(source_link)
        #print(source, mapping_screening_tool)
        if source in mapping_screening_tool:
            for screening_tool, url in zip(mapping_screening_tool[source][0], mapping_screening_tool[source][1]):
                response += "<br><br> These screening tools might also be helpful: <a href='" + url + "' target='_blank'>"+screening_tool+"</a>"
    #print(response)
    return response


@app.route('/sendMessage', methods=['POST'])
def handle_message():
    data = request.json  # Get the JSON data sent from the frontend
    message = data['message']  # Extract the message from the JSON data
    print("The current conversation history: ")
    print(session["conversation_history"])

    response_message = get_chatbot_response(message)

    # Return the response message
    return jsonify({'response': response_message})
