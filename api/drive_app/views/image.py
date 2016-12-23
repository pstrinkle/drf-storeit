from rest_framework import viewsets
from rest_framework.metadata import SimpleMetadata

from drive_app.serializers import ImageSerializer
from drive_app.models import Image, alphanumeric


class ImageMetadata(SimpleMetadata):
    """
    Custom Metadata handler to get the regex validator output into the options.
    """

    def determine_metadata(self, request, view):
        metadata = super(ImageMetadata, self).determine_metadata(request, view)

        if 'actions' in metadata and 'POST' in metadata['actions']:
            if 'name' in metadata['actions']['POST']:
                metadata['actions']['POST']['name']['pattern'] = alphanumeric.regex.pattern

        return metadata


class ImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Images to be viewed or edited.
    """

    metadata_class = ImageMetadata
    serializer_class = ImageSerializer

    def get_queryset(self):
        """
        Make it so an owner can only retrieve or list their own Images.
        """

        qs = Image.objects.all()
        qs.filter(owner=self.request.user)
        return qs

