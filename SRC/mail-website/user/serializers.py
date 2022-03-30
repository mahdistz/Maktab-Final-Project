from rest_framework import serializers
from .models import Contact, Users


class ContactSerializer(serializers.ModelSerializer):
    # for foreign_key fields
    email = serializers.StringRelatedField(read_only=True, required=False)

    class Meta:
        model = Contact
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['username']
        # exclude = ['password', 'last_login', 'date_joined', 'groups', 'user_permissions']
