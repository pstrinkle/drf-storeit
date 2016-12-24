from rest_framework import status
from rest_framework.test import APIClient
from drive_app.models import DriveUser
from drive_app.tests.base import BasicTest


class FolderListTests(BasicTest):

    def setUp(self):
        self.superuser = DriveUser.objects.create_superuser('john@snow.com', 'password123')

        self.login(username='john@snow.com')
        self.one_id = self.create_user('one@snow.com')
        self.two_id = self.create_user('two@snow.com')
        self.logout()

    def test_can_list_root_folders(self):
        """
        Admin can list all root folders.
        """

        self.login(username='john@snow.com')
        response = self.client.get('/api/v1/folder', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(6, len(response.data))
        self.logout()

    def test_can_list_only_my_folders(self):
        """
        A user can only list their own folders.
        """

        self.login(username='one@snow.com')
        response = self.client.get('/api/v1/folder', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data))  # root and trash.
        self.logout()

