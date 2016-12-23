from rest_framework import status
from drive_app.models.models import DriveUser
from drive_app.tests.catotest import BasicTest


class MessageCreateTests(BasicTest):

    def setUp(self):
        self.superuser = DriveUser.objects.create_superuser('admin', 'john@snow.com', 'password123')
        self.login(username='admin')



        self.logout()

    def test_can_create_root_level_folder(self):
        """
        Folder without a parent folder.
        """

        self.login(username='user_a')
        response = self.client.post('/api/v1/folder', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.verify_built({}, response.data)
        self.logout()

