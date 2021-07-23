#Used to create the database and auxiliary class to add, query and remove elements in the tables
from app import db
from werkzeug.security import check_password_hash, generate_password_hash

#Defines the user table and methods to create, and search users in the database
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    @classmethod
    def find_user(cls, username):
        """Searches the user table for by username"""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_user_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first()

    def register_user(self):
        """Adds a new user to the database"""
        db.session.add(self)
        db.session.commit()

#Defines the chatroom table and methods to create, delete and search for chatrooms in the database
class Chatroom(db.Model):
    __tablename__ = 'chatroom'
    id = db.Column(db.Integer, primary_key=True)
    chatroom_name = db.Column(db.String(), unique=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False,)
    created = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    def __init__(self, chatroom_name, author_id):
        self.chatroom_name = chatroom_name
        self.author_id = author_id

    @classmethod
    def get_chatrooms(cls):
        """Searches a joined table from the three DB tables for all the available chatrooms"""
        chatrooms = cls.query.join(User, Chatroom.author_id == User.id).order_by(Chatroom.chatroom_name.desc()).all()
        return chatrooms

    @classmethod
    def get_chatroom(cls, chatroom_id):
        """Searches a joined table from the three DB tables for a chatroom with given id"""
        chatroom = cls.query.join(User, Chatroom.author_id == User.id).filter(Chatroom.id == chatroom_id).first()
        return chatroom

    def delete_chatroom(self):
        db.session.delete(self)
        db.session.commit()

    def add_chatroom(self):
        db.session.add(self)
        db.session.commit()

#Defines the message table and methods to create and delete messages, also to retrieve
#all the messages posted in a given chatroom
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.String, db.ForeignKey(User.id), nullable=False, )
    created = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    content = db.Column(db.String, nullable=False)
    command = db.Column(db.String, default="notgiven")
    chatroom_id = db.Column(db.Integer, db.ForeignKey(Chatroom.id), nullable=False, )

    def __init__(self, author_id, content, command, chatroom_id):
        self.author_id = author_id
        self.content = content
        self.command = command
        self.chatroom_id = chatroom_id

    @classmethod
    def get_messages(cls, chatroom_id):
        """Searches the message table for all the messages posted in a given chatroom, 
        limiting the search to the 50 most recent messages to be showned to the users"""
        messages = cls.query.join(Chatroom, Chatroom.id == Message.chatroom_id)\
                            .filter(Message.chatroom_id == chatroom_id)\
                            .order_by(Message.created.asc()).limit(50).all()
        return messages

    def add_message(self):
        db.session.add(self)
        db.session.commit()

    def delete_message(self):
        db.session.delete(self)
        db.session.commit()

def init_db():
    """Initializes the database, when it is empty, and creates the bot user that posts the stock broadcasts"""
    db.create_all()
    if User.find_user('stockbot') is None:
        userObj = User('stockbot', generate_password_hash('stockbot'))
        userObj.register_user()