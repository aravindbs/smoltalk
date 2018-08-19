from app import app,socketio,mongo
from flask_cors import CORS, cross_origin
from flask import render_template, url_for, request, redirect, flash, Response
from flask_login import login_user, login_required,current_user, logout_user,login_manager
from .login_handler import User
import datetime, os, pymongo, json
from bson import json_util
from werkzeug.security import generate_password_hash, check_password_hash

#CORS(app, support_credentials= True)
@app.route('/', methods = ['GET' , 'POST'])
#@cross_origin(supports_credentials=True)
def login():
    if request.method == 'POST':
        login_data = request.form.to_dict()
        user = mongo.db.users.find_one({'email' : login_data['email']})
        if user:
            if check_password_hash(user['password'], login_data['password']):
                user_obj = User(user)
                login_user (user_obj)
                flash('Login Successful')
                return redirect(url_for('chat', user= user['username']))
            else:
                flash("Incorrect Password")
                return redirect (url_for('login'))
        else:
            flash("Invalid Username. Try Again")
            return redirect (url_for('login'))
    test = render_template ('login.html')
    print type (test)
    return test


@app.route('/signup', methods= ['GET' , 'POST'])
#@cross_origin(supports_credentials=True)
def signup():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        hashed_pwd = generate_password_hash(form_data['password'])
        new_user = { 'email' : form_data['email'], 'username' : form_data['username'], 'password' : hashed_pwd }
        if mongo.db.users.find_one({ 'email' : new_user['email']}):
            flash("Username Exists, Try Again")
            return redirect ( url_for('signup'))
        else :
            mongo.db.users.insert_one(new_user)
            user = User (mongo.db.users.find_one({'username' : new_user['username']}) )
            login_user(user)
            return redirect (url_for('chat'))
    return render_template('signup.html')



@app.route("/chat")
#@cross_origin(supports_credentials=True)
@login_required
def chat(): 
    query = mongo.db.users.find()
    users = json.dumps(list(query), default=json_util.default)
   # print users
    base_url = request.url_root
    print base_url
    return render_template('chat.html', username = current_user.username, users = users, base_url = base_url)


@app.route("/logout")
#@cross_origin(supports_credentials=True)
def logout():
    mongo.db.sessions.delete_many({'username' : current_user.username })
    logout_user()
    return redirect(url_for('login'))


def to_client(message):
    query = { 'username' : message['to_id']}
    active_sessions = mongo.db.sessions.find(query)
    for session in active_sessions:
        print "sent to {}".format(session['username'])
        socketio.emit('to_event', json.dumps(message, default = json_util.default), room = session['session_id'], namespace='/send')


@app.route("/api/messages", methods = ['GET' , 'POST'])
#@cross_origin(supports_credentials=True)
#@login_required
def messages():
    if request.method == "GET":
        from_id = request.args.get('from_id')
        to_id = request.args.get('to_id')
        no_of_msgs = int (request.args.get('no_of_msgs'))
        query = mongo.db.messages.find( { '$or' : [{ 'from_id' : from_id, 'to_id' : to_id }, {'to_id' : from_id, 'from_id' : to_id }]}).sort('timestamp', pymongo.DESCENDING).limit(no_of_msgs)
        msgs = list(query)
        msgs.reverse()
        messages = json.dumps( msgs, default=json_util.default)
        return messages


    if request.method == "POST":
        data = request.get_json(force = True)
        data['timestamp'] = datetime.datetime.now()
        mongo.db.messages.insert_one(data)
        resp = Response ("Message Sent", mimetype='application/text', status=201)
        return resp


@socketio.on('connect', namespace='/send')
#@cross_origin(supports_credentials=True)
@login_required
def connect():
    print "{} connected".format(current_user.username)
    new_session = { 'username' : current_user.username }
    mongo.db.sessions.update(new_session,{'username' : current_user.username ,'session_id' : request.sid}, upsert=True )


@socketio.on('disconnect', namespace='/send')
#@cross_origin(supports_credentials=True)
@login_required
def disconnect():
    query = { "session_id" : request.sid }
    mongo.db.sessions.delete_one(query)


@socketio.on('from_event', namespace='/recv')
#@cross_origin(supports_credentials=True)
@login_required
def from_message(new_message):
    if new_message:
        new_message = json.loads(new_message)
        print type( new_message)
        new_message['timestamp'] = datetime.datetime.now()
        print new_message
        mongo.db.messages.insert_one(new_message)
        to_client (new_message)


#######Prevents cacehing of static files in the browser#######
@app.context_processor
#@cross_origin(supports_credentials=True)
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)
##############################################################