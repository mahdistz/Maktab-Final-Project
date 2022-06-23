from rest_framework import serializers
from .models import Email, Category
from user.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class EmailSerializer(serializers.ModelSerializer):
    # for foreign_key fields
    sender = UserSerializer(read_only=True)
    signature = serializers.StringRelatedField(read_only=True, required=False)

    class Meta:
        model = Email
        exclude = ['cc', 'bcc']

    # for many_to_manny fields
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["recipients"] = UserSerializer(instance.recipients.all(), many=True).data
        rep["category"] = CategorySerializer(instance.category.all(), many=True).data
        return rep
