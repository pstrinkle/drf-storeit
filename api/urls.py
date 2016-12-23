"""image_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_nested import routers as nrouters

from django.conf import settings
from django.conf.urls.static import static

from drive_app.views import folder
from drive_app.views import image
from drive_app.views import user

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'user', user.UserViewSet, base_name='user')
router.register(r'folder', folder.FolderViewSet, base_name='folder')
router.register(r'image', image.ImageViewSet, base_name='image')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^api/(?P<version>(v1))/', include([
        url(r'^', include(router.urls)),
    ])),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'auth/', include('knox.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
