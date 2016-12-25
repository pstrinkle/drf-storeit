from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response


from drive_app.serializers import FileSerializer
from drive_app.models import MiscFile


class FileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Images to be viewed or edited.
    """

    serializer_class = FileSerializer

    def get_queryset(self):
        """
        Make it so an owner can only retrieve or list their own Images.
        """

        qs = MiscFile.objects.filter(owner=self.request.user.id)
        return qs

    def partial_update(self, request, pk=None, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)
