from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinLengthValidator

from easy_thumbnails.signals import saved_file
from easy_thumbnails.signal_handlers import generate_aliases_global
from easy_thumbnails import fields

from sanitizer.models import SanitizedCharField, SanitizedTextField

#saved_file.connect(generate_aliases_global)

alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
minlength = MinLengthValidator(3, message='Field value must be at least 3 characters long')


class DriveUser(AbstractUser):
    """
    Our custom user.
    """

    # this is a dup field for date_joined (default)
    added = models.DateTimeField(auto_now_add=True)


class Folder(models.Model):
    """
    How we organize images.
    """

    added = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey('DriveUser', related_name='folders')
    folder = models.ForeignKey('Folder', related_name='folders')

    name = SanitizedCharField(max_length=256, validators=[alphanumeric, minlength])

    class Meta:
        # Make sure you can't add the same Target for a customer twice.
        unique_together = ('owner', 'name')


class Image(models.Model):
    """
    How we store the image.
    """

    added = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey('DriveUser', related_name='images')
    folder = models.ForeignKey('Folder', related_name='images')

    name = SanitizedCharField(max_length=256, validators=[alphanumeric, minlength])
    size = models.IntegerField(default=0)

    # How we track stored images.
    file = models.ImageField()
    thumbnail = fields.ThumbnailerImageField(upload_to='thumbnails',
                                             resize_source=dict(size=(160, 160), sharpen=True),
                                             blank=True)


