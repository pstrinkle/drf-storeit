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
        validated_data['owner'] = self.context['request'].user

        img = Image.objects.create(**validated_data)

        return img

    class Meta:
        model = apps.get_model('drive_app.Image')
        fields = ('size', 'added', 'owner', 'folder', 'file', 'id', 'thumbnail', 'name')
        read_only_fields = ('size', )


class ImageSubSerializer(serializers.HyperlinkedModelSerializer):
    """
    Sub-view serializer.
    """

    thumbnail = serializers.SerializerMethodField(read_only=True)

    def get_thumbnail(self, obj):
        """
        I wrote this because it (by default) returns the full path, and with nginx serving the media and static, it
        is unhappy.  Also, this working when running directly via manage.py  So, win-win.
        """

        return obj.thumbnail.url

    class Meta:
        model = apps.get_model('drive_app.Image')
        fields = ('name', 'id', 'thumbnail')


class FolderSubSerializer(serializers.HyperlinkedModelSerializer):
    """
    Sub-view serializer.
    """

    class Meta:
        model = apps.get_model('drive_app.Folder')
        fields = ('name', 'id')


class FolderSerializer(serializers.HyperlinkedModelSerializer):
    """
    RW Folder serializer.

    If folder is blank, it's basically treated as a root level folder.
    Owner should be blank, we fill it in with the request maker's id.
    """

    # XXX We shouldn't return the full list, since we should respect the hierarchy.
    images = ImageSubSerializer(many=True, read_only=True)
    folders = FolderSubSerializer(many=True, read_only=True)

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
        validated_data['owner'] = self.context['request'].user

        if 'folder' not in validated_data:
            root = Folder.objects.get(name='_', owner=self.context['request'].user.id)
            validated_data['folder'] = root

        folder = Folder.objects.create(**validated_data)

        return folder

    class Meta:
        model = apps.get_model('drive_app.Folder')
        fields = ('added', 'owner', 'folder', 'name', 'images', 'folders', 'id')


class DriveUserSerializer(serializers.HyperlinkedModelSerializer):
    """
    RW ImageUser serializer.
    """

    # XXX We shouldn't return the full list, since we should respect the hierarchy.
    #images = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    #folders = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    # input
    password = serializers.CharField(
        write_only=True,
        style={
            'input_type': 'password',
            'placeholder': 'Password'
        }
    )

    root = serializers.SerializerMethodField(read_only=True)

    def get_root(self, obj):
        return Folder.objects.get(owner=obj.id, name='_').id

    def create(self, validated_data):
        """
        Create the user.
        """

        email = validated_data['email']
        password = validated_data['password']
        del validated_data['email']
        del validated_data['password']

        user = DriveUser.objects.create_user(email=email, password=password, **validated_data)

        return user

    class Meta:
        model = apps.get_model('drive_app.DriveUser')
        fields = ('email', 'password', 'first_name', 'last_name', 'root', 'id')
        write_only_fields = ('password',)


class LoginUserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Login output serializer.
    """

    root = serializers.SerializerMethodField(read_only=True)

    def get_root(self, obj):
        return Folder.objects.get(owner=obj.id, name='_').id

    class Meta:
        model = apps.get_model('drive_app.DriveUser')
        fields = ('email', 'first_name', 'last_name', 'root', 'id')

