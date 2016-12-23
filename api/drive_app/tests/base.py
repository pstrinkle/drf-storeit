from rest_framework import status
from rest_framework.test import APITestCase

from drive_app.models import DriveUser
from random import choice
from json import dumps
import string
import os


class BasicTest(APITestCase):
    """
    Generic testing stuff.
    """

    PW = 'password123'

    def login(self, username):
        self.client.login(username=username, password=self.PW)

    def logout(self):
        self.client.logout()

    def verify_built(self, expected, data):
        for key in expected:
            self.assertEqual(data[key], expected[key])

    def create_user(self, email):
        """
        Create a basic user for testing.
        """

        user = {
            'email':      email,
            'first_name': 'first',
            'last_name':  'last',
            'password':   self.PW,
        }

        response = self.client.post('/api/v1/user', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        del user['password']
        self.verify_built(user, response.data)
        return response.data['id']

