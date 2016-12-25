from django.shortcuts import get_object_or_404
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

    def update(self, request, pk=None, **kwargs):
        """
        """

        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=pk)

        # don't let them change the owner.
        data = request.data.copy()
        data['owner'] = obj.owner.id

        serializer = FileSerializer(obj, data=data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
