from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from drive_app.serializers import DriveUserSerializer
from drive_app.models import DriveUser


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    serializer_class = DriveUserSerializer

    def get_queryset(self):
        """
        Make it so an owner can only retrieve or list their own Folders.
        """

        if self.request.user.is_superuser:
            qs = DriveUser.objects.all()
        else:
            qs = DriveUser.objects.filter(id=self.request.user.id)

        return qs

    def partial_update(self, request, pk=None, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['post'])
    def secondarylogin(self, request, *args, **kwargs):
        """
        Login for sessionid with API for storing the cookies.
        """

        # Get the parameters from the request
        username = request.data['username']
        password = request.data['password']
        remember = request.data.get('remember', False)

        # I don't imagine I need to pass the username and password for this to work. :D

        # Attempt authentication
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # set the expiration to 0 if remember wasn't requested
                if not remember:
                    request.session.set_expiry(0)
                return HttpResponse(self.serializer_class(user).data)
            else:
                return HttpResponse(status=status.HTTP_403_FORBIDDEN)
        else:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

