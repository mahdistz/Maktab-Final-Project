from rest_framework import serializers
from .models import Contact, Users


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        exclude = ['password', 'verification', 'last_login', 'date_joined', 'groups', 'user_permissions']


class ContactSerializer(serializers.ModelSerializer):
    # for foreign_key fields
    email = serializers.StringRelatedField(read_only=True, required=False)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Contact
        fields = '__all__'
