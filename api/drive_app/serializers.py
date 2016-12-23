from django.apps import apps
from rest_framework import serializers

from drive_app.models import *


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    """
    RW Image serializer.
    """

    owner = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('drive_app.DriveUser').objects.all(), required=False
    )
    folder = serializers.PrimaryKeyRelatedField(queryset=apps.get_model('drive_app.Folder').objects.all())

    thumbnail = serializers.SerializerMethodField(read_only=True)

    def get_thumbnail(self, obj):
        """
        I wrote this because it (by default) returns the full path, and with nginx serving the media and static, it
        is unhappy.  Also, this working when running directly via manage.py  So, win-win.
        """

        return obj.thumbnail.url

    def validate_folder(self, value):
        """
        Verify you own this folder.
        """

        if value.owner.id != self.context['request'].user.id:
            raise serializers.ValidationError("You must specify a Folder you own.")

        return value

    def create(self, validated_data):
        validated_data['size'] = validated_data['file'].size
        validated_data['thumbnail'] = validated_data['file']
        # Make it you can only create files into your own folders.
        validated_data['owner'] = self.context['request'].user.id

        img = Image.objects.create(**validated_data)

        return img

    class Meta:
        model = apps.get_model('drive_app.Image')
        fields = ('size', 'added', 'owner', 'folder', 'file', 'id', 'thumbnail', 'name')
        read_only_fields = ('size', )


class FolderSerializer(serializers.HyperlinkedModelSerializer):
    """
    RW Folder serializer.

    If folder is blank, it's basically treated as a root level folder.
    """

    owner = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('drive_app.DriveUser').objects.all(), required=False
    )
    folder = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('drive_app.Folder').objects.all(), required=False
    )

    def validate_folder(self, value):
        """
        Verify you own this folder.
        """

        if value.owner.id != self.context['request'].user.id:
            raise serializers.ValidationError("You must specify a Folder you own.")

        return value

    def create(self, validated_data):
        # Make it you can only create folders into your own folders.
        validated_data['owner'] = self.context['request'].user.id

        if 'folder' not in validated_data:
            pass  # XXX: Point it at the root folder.

        folder = Folder.objects.create(**validated_data)

        return folder

    class Meta:
        model = apps.get_model('drive_app.Folder')
        fields = ('added', 'owner', 'folder', 'name', 'id')


class DriveUserSerializer(serializers.HyperlinkedModelSerializer):
    """
    RW ImageUser serializer.
    """

    # input
    password = serializers.CharField(
        write_only=True,
        style={
            'input_type': 'password',
            'placeholder': 'Password'
        }
    )

    def create(self, validated_data):
        """
        Create the user.
        """

        user = DriveUser.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = apps.get_model('drive_app.DriveUser')
        fields = ('added', 'email', 'username', 'password', 'first_name', 'last_name', 'id')
        write_only_fields = ('password',)


class LoginUserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Login output serializer.
    """

    class Meta:
        model = apps.get_model('drive_app.DriveUser')
        fields = ('email', 'username', 'first_name', 'last_name', 'id')

