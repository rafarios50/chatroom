import unittest
from flask import request, make_response, redirect, render_template, session, url_for, flash

from app import create_app

#Create the app from __init__ in app folder
app = create_app()

#Definition of a command line to perform tests of the application
@app.cli.command()
def test():
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner().run(tests)