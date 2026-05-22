from rest_framework import serializers
from .models import CustomUser, ProfileViewLog

class UserSerializer(serializers.ModelSerializer):
    # Enforce clear validation constraints for incoming registration bodies
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    gender = serializers.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=True)
    age = serializers.IntegerField(required=True, min_value=18)
    
    # Custom read-only field computed at runtime
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'first_name',  # Added
            'last_name',   # Added
            'full_name',   # Added
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

    def get_full_name(self, obj):
        # Safely constructs full name or defaults to username
        f_name = getattr(obj, 'first_name', '') or ''
        l_name = getattr(obj, 'last_name', '') or ''
        combined = f"{f_name} {l_name}".strip()
        return combined if combined else obj.username

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
    # This automatically picks up full_name now because it nests the updated UserSerializer!
    visitor_details = UserSerializer(source='visitor', read_only=True)

    class Meta:
        model = ProfileViewLog
        fields = ['id', 'visitor_details', 'timestamp']