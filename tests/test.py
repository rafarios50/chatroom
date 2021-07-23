from flask_testing import TestCase
from flask import url_for
import unittest

from main import app

#Script that manages the unit test defined for the flask app

class MainTest(TestCase):
    def create_app(self):
        """Creates the testing environment"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def test_app_exists(self):
        """Tests if the app is being created"""
        self.assertIsNotNone(app)

    def test_app_in_test_mode(self):
        """Tests if the app is being executed in test mode"""
        self.assertTrue(app.config['TESTING'])

    def test_auth_blueprint_exists(self):
        """Test if the authentication blueprint exists"""
        self.assertIn('auth', self.app.blueprints)

    def test_chatroom_blueprint_exists(self):
        """Test if the chatroom blueprint exists"""
        self.assertIn('chatroom', self.app.blueprints)

    def test_auth_login_get(self):
        """Tests if the client can access the login page"""
        response = self.client.get(url_for('auth.login'))
        self.assert200(response)

    def test_auth_register_post(self):
        """Tests if a user is registered correctly, this test will fail if the user is already registered"""
        user_form = {
            'username': 'test_user',
            'password': 'test_password'
        }
        response = self.client.post(url_for('auth.register'), data=user_form)
        self.assertRedirects(response, url_for('auth.login'))

    def test_auth_login_post(self):
        """Tests if a user is redirected to the index page after being succesfully logged in.
        Fails if the test_user has not been registered"""
        user_form = {
            'username': 'test_user',
            'password': 'test_password'
        }
        response = self.client.post(url_for('auth.login'), data=user_form)
        self.assertRedirects(response, url_for('index'))
