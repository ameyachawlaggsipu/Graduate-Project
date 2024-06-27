from flask import Flask

app = Flask(__name__)
app.secret_key = 'random_secret_key'  # Set to a random secret value

from chatbot_application import routes