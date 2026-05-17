from rest_framework import serializers
from .models import CustomUser, ProfileViewLog


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser

        fields = [
            'id',
            'username',
            'email',
            'age',
            'cast',
            'location',
            'gender',
            'preferences',
            'bio',
            'password',
        ]

        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': False
            }
        }

    def create(self, validated_data):

        password = validated_data.pop('password', None)

        user = CustomUser(**validated_data)

        if password:
            user.set_password(password)

        user.save()

        return user

    def update(self, instance, validated_data):

        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        return instance
    
class ProfileViewLogSerializer(serializers.ModelSerializer):
    visitor_details = UserSerializer(source='visitor', read_only=True)

    class Meta:
        model = ProfileViewLog
        fields = ['id', 'visitor_details', 'timestamp']