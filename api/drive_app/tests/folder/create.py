from rest_framework import status
from rest_framework.test import APIClient
from drive_app.models import DriveUser
from drive_app.tests.base import BasicTest


class FolderCreateTests(BasicTest):

    def setUp(self):
        self.superuser = DriveUser.objects.create_superuser('john@snow.com', 'password123')

        self.login(username='john@snow.com')
        self.one_id = self.create_user('one@snow.com')
        self.two_id = self.create_user('two@snow.com')
        self.logout()

    def test_can_create_root_level_folder(self):
        """
        Folder without a parent folder.
        """

        folder = {
            'name': 'new',
        }

        client = APIClient()
        client.login(username='one@snow.com', password=self.PW)

        response = client.post('/api/v1/folder', folder, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        folder['owner'] = self.one_id

        self.verify_built(folder, response.data)
        client.logout()

    def test_can_create_subordinate_folder(self):
        """
        Verify you can create a folder under a folder under the root folder.
        """

    def test_cant_create_folder_under_another_user(self):
        """
        Verify if owner is specified, it's ignord.
        """

