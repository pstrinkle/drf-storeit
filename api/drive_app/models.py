from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, MinLengthValidator
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager

from easy_thumbnails.signals import saved_file
from easy_thumbnails.signal_handlers import generate_aliases_global
from easy_thumbnails import fields

from sanitizer.models import SanitizedCharField, SanitizedTextField

#saved_file.connect(generate_aliases_global)

alphanumeric = RegexValidator(r'^[\.0-9a-zA-Z_]*$', 'Only alphanumeric characters are allowed.')
minlength = MinLengthValidator(3, message='Field value must be at least 3 characters long')


class Folder(models.Model):
    """
    How we organize images.
    """

    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey('DriveUser', related_name='folders')
    folder = models.ForeignKey('Folder', blank=True, null=True, related_name='folders')

    name = SanitizedCharField(max_length=256, validators=[alphanumeric, minlength])

    class Meta:
        # imperfect because then you can't have subordinate directories with the same name...
        unique_together = ('owner', 'name')


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.owner.id, filename)


class MiscFile(models.Model):
    """
    How we store the files.
    """

    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey('DriveUser', blank=True, null=True, related_name='files')
    folder = models.ForeignKey('Folder', related_name='files')

    name = SanitizedCharField(max_length=256, validators=[minlength])
    size = models.IntegerField(default=0)

    file = models.FileField(upload_to=user_directory_path)


class Image(models.Model):
    """
    How we store the image.
    """

    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey('DriveUser', blank=True, null=True, related_name='images')
    folder = models.ForeignKey('Folder', related_name='images')

    name = SanitizedCharField(max_length=256, validators=[minlength])
    size = models.IntegerField(default=0)

    # How we track stored images.
    file = models.ImageField()
    thumbnail = fields.ThumbnailerImageField(upload_to='thumbnails',
                                             resize_source=dict(size=(120, 120), sharpen=True),
                                             blank=True)


class DriveUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_root(self, user):
        """
        Create a root directory for the user.
        """

        # This name value violates the validators.
        params = {
            'owner': user,
            'name': '_'
        }

        root = Folder.objects.create(**params)
        root.save(using=self._db)

        params['name'] = '.trash'

        root = Folder.objects.create(**params)
        root.save(using=self._db)

    def _create_user(self, email, password, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """

        email = self.normalize_email(email).lower()

        # for the admin view.
        if is_superuser:
            extra_fields['is_staff'] = True

        user = self.model(email=email, is_active=True, is_superuser=is_superuser, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        self._create_root(user)
        return user

    def create_user(self, email, password=None, **extra_fields):
        if 'email' in extra_fields:
            del extra_fields['email']

        return self._create_user(email, password, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, **extra_fields)


class DriveUser(AbstractBaseUser, PermissionsMixin):
    """
    AbstractBaseUser has no fields beyond permissions fields.
    AbstractUser provides a full user profile however can't be used with a custom
    Manager.
    """

    # Base Fields
    email = models.EmailField(unique=True)
    first_name = SanitizedCharField(max_length=48, validators=[minlength])
    last_name = SanitizedCharField(max_length=48, validators=[minlength])

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = DriveUserManager()
    USERNAME_FIELD = 'email'
    # required for creating superuser (+username_field)
    REQUIRED_FIELDS = []

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name


