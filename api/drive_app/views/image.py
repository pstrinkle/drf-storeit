from rest_framework import viewsets

from drive_app.serializers import ImageSerializer
from drive_app.models import Image


class ImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Images to be viewed or edited.
    """

    serializer_class = ImageSerializer

    def get_queryset(self):
        """
        Make it so an owner can only retrieve or list their own Images.
        """

        qs = Image.objects.all()
        qs.filter(owner=self.request.user)
        return qs

