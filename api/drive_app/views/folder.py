from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from rest_framework.decorators import detail_route
from rest_framework import status
from rest_framework import viewsets
from rest_framework.metadata import SimpleMetadata

from drive_app.serializers import FolderSerializer
from drive_app.models import Folder, alphanumeric


class FolderMetadata(SimpleMetadata):
    """
    Custom Metadata handler to get the regex validator output into the options.
    """

    def determine_metadata(self, request, view):
        metadata = super(FolderMetadata, self).determine_metadata(request, view)

        if 'actions' in metadata and 'POST' in metadata['actions']:
            if 'name' in metadata['actions']['POST']:
                metadata['actions']['POST']['name']['pattern'] = alphanumeric.regex.pattern

        return metadata


class FolderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that lets a user manipulate their folders.
    """

    serializer_class = FolderSerializer

    def get_queryset(self):
        """
        Make it so an owner can only retrieve or list their own Folders.
        """

        qs = Folder.objects.all()
        qs.filter(owner=self.request.user)
        return qs


