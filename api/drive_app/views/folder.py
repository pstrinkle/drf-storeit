from rest_framework import status
from rest_framework import viewsets
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response

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

    metadata_class = FolderMetadata
    serializer_class = FolderSerializer

    def get_queryset(self):
        """
        Make it so an owner can only retrieve or list their own Folders.
        """

        if self.request.user.is_superuser:
            qs = Folder.objects.all()
        else:
            qs = Folder.objects.filter(owner=self.request.user.id)

        return qs

    def partial_update(self, request, pk=None, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request, **kwargs):
        """
        Create a Folder
        """

        update_these = request.data.copy()
        update_these['owner'] = request.user.id

        serializer = FolderSerializer(data=update_these, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
