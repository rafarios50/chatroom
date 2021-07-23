from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
from werkzeug.exceptions import abort
import re
import requests

from app.auth import login_required
from app.dbschema import Chatroom, Message, User

#Blueprint in charge of the chatroom app
bp = Blueprint('chatroom', __name__)

@bp.route('/')
def index():
    """Load the available chatrooms and renders the index page with them"""
    chatrooms = Chatroom.get_chatrooms()
    return render_template('index.html', chatrooms=chatrooms)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Creates a new chatroom. Every user is able to create new chatrooms."""
    if request.method == 'POST':
        title = request.form['title']
        error = None
        if not title:
            error = 'Title is required.'
        if error is not None:
            flash(error)
        else:
            chatroomObj = Chatroom(title, g.user.id)
            chatroomObj.add_chatroom()
            return redirect(url_for('index'))
    return render_template('chatroom/create.html')

@bp.route('/delete/<int:id>', methods=('POST',))
@login_required
def delete(id):
    """Deletes a chatroom, only the user that create the chatroom can delete it"""
    #Deletes all the messages posted in the chatroom before deleting it
    messages = Message.get_messages(id)   
    for m in messages:
        m.delete_message()
    chatroomObj = Chatroom.get_chatroom(id)
    chatroomObj.delete_chatroom()
    return redirect(url_for('index'))

def parse_stock_command(content, users, chatroom_id):
    """Tries to parse a command sent by a user in a post.
    Returns true if the message was parsed correctly and False otherwise.
    If the command is parsed correctly, a message is created by bot user in the given chatroom"""
    stock_code = re.findall('/stock=(.+)', content)[0]
    print(stock_code)
    try:
        csv = requests.get(f'https://stooq.com/q/l/?s={stock_code}&f=sd2t2ohlcv&h&e=csv', stream=True)
        header, data = csv.text.strip().split()
        data = data.split(',')
        if data[4] != 'N/D':
            high_value = float(data[4])                
        else:
            high_value = 'N/D'
        stockbot_userObj = User.find_user('stockbot')
        messageObj = Message(stockbot_userObj.id, f'{stock_code} quote is ${high_value} per share.', '/stock', chatroom_id)
        messageObj.add_message()
        return (True, messageObj)
    except:
        print(f'command given in {content} is unknown')
        return (False, None)


@bp.route('/chatroom/<int:id>', methods=('GET', 'POST'))
@login_required
def join(id):
    """Renders the given chatroom page and allows user to post new messages.
    If the message might include a command (message content starts with /),
    it is parsed by parse_stock_command function, otherwise the message is posted."""
    messages = Message.get_messages(id)
    chatroom = Chatroom.get_chatroom(id)
    #creates a dictionary of user.id: user.username to be used when showing the messages in the chat
    users = {}
    for m in messages:
        try:
            users[m.author_id] = User.find_user_by_id(m.author_id).username
        except:
            print(f'User with id {m.author_id} was not found in the database')
    #if a new meesage is posted to the chatroom
    if request.method == 'POST':
        content = request.form['content']
        #check if it is a command
        if content[0] == '/':
            command_parsed, new_message = parse_stock_command(content, users, id)
            if command_parsed:
                messages.append(new_message)
                render_template('chatroom/chatroom.html', chatroom=chatroom, messages=messages, users=users)
            else:
                flash('Given command was not understood, please try again.')
                render_template('chatroom/chatroom.html', chatroom=chatroom, messages=messages, users=users)
        else:
            command='none'
            messageObj = Message(g.user.id, content, command, id)
            messageObj.add_message()
            messages.append(messageObj)
            render_template('chatroom/chatroom.html', chatroom=chatroom, messages=messages, users=users)
    return render_template('chatroom/chatroom.html', chatroom=chatroom, messages=messages, users=users)
    