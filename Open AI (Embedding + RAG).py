import sys
import os
import sys
from dotenv import load_dotenv
import os
os.environ["OPENAI_API_KEY"] = ""
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

documents = []
# Create a List of Documents from all of our files in the ./docs folder
for file in os.listdir("C:/Users/USER/Desktop/Graduate_Project/docs"):
    if file.endswith(".pdf"):
        pdf_path = "./docs/" + file
        loader = PyPDFLoader(pdf_path)
        documents.extend(loader.load())
  

vectordb = Chroma.from_documents(documents, embedding=OpenAIEmbeddings(), persist_directory="./data")
vectordb.persist()



# Initialize the PDF question-answering chain
pdf_qa = ConversationalRetrievalChain.from_llm(
    ChatOpenAI(temperature=0.7, model_name='gpt-3.5-turbo'),
    retriever=vectordb.as_retriever(search_kwargs={'k': 1}),
    return_source_documents=True,
    verbose=False
)

# Define color codes for terminal output
yellow = ""
green = ""
white = ""

# Initialize chat history

chat_history = []

# Print welcome message
print(f"{yellow}---------------------------------------------------------------------------------")
print('Welcome to the PyschBot')
print('---------------------------------------------------------------------------------')
print(f"{white}")

# Main interaction loop
try:
    while True:
        query = input(f"{green}Patient: {white} ")
        print('\n')
        
        # Check for exit commands
        if query.lower() in ["exit", "quit", "q", "f"]:
            print('Exiting')
            break
        
        # Skip empty queries
        if query == '':
            continue
        
        # Invoke the PDF question-answering model
        result = pdf_qa.invoke(
            {"question": query, "chat_history": chat_history}
        )
        
        # Print the answer
        print("Mental Assistant:")
        for chunk in result['answer']:
        # Split the chunk by full stop and rejoin with a full stop and a newline
        # This adds a newline after each sentence
            processed_chunk = chunk.replace(". ", ".\n")
            print(processed_chunk, end="", flush=True)
        print('\n')

        
        # Update chat history
        chat_history.append((query, result["answer"]))
except KeyboardInterrupt:
    print('\nProgram exited by user.')
