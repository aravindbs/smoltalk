from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_pymongo import PyMongo

## Update file while deploying 
app = Flask(__name__)
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
app.secret_key = "abc"
app.config["MONGO_URI"] = "mongodb://localhost:27017/testdb2"
mongo = PyMongo (app)
from app import views,login_handler,words
