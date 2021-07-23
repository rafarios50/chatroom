# Chatroom
Web chat application in Flask

# Installation for Windows through CMD

Setup a python environment:

>python -m venv venv

>venv\Scripts\activate

Install dependencies:
>pip install -r requirements.txt

Set Flask environment:
>set FLASK_APP=main

Run the application
>flask run

Access the aplication through http://127.0.0.1:5000

# Application description

The application allows registered user to log in and create or join available chatrooms.

Additionally, users can broadcast informative messages about a stock of interest to the chatroom, when using the /stock=stock_code command.

The stock_code is used to request stock information from the page https://stooq.com/

