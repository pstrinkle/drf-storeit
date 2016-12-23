
from rest_framework import status
from rest_framework.test import APITestCase

from drive_app.models.models import DriveUser
from json import dumps
import os
from random import choice
import string


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

