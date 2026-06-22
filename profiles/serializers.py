from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import CustomUser, ProfileViewLog


class UserSerializer(serializers.ModelSerializer):
    # Enforce clear validation constraints for incoming registration bodies
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    phone_number = serializers.CharField(
        required=True,
        max_length=10,
        validators=[
            UniqueValidator(
                queryset=CustomUser.objects.all(),
                message="An account with this phone number is already registered.",
            )
        ],
    )
    gender = serializers.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=True)
    age = serializers.IntegerField(required=True, min_value=18)

    # Custom read-only field computed at runtime
    full_name = serializers.SerializerMethodField()
    album = serializers.SerializerMethodField()

    # photos_data = serializers.ListField(
    #     child=serializers.DictField(), write_only=True, required=False
    # )
    profile_picture = serializers.SerializerMethodField()
    verification_status = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "email",
            "age",
            "cast",
            "location",
            "gender",
            "preferences",
            "bio",
            "password",
            "profile_picture",
            "is_verified",
            "verification_status",
            "is_staff",
            "album",
            "is_hidden",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "username": {"read_only": True},
        }
    
    def validate_email(self, value):
        # 1. Skip validation if the user leaves the email blank
        if not value:
            return value
            
        # 2. Check for case-insensitive duplicates, ignoring the current user 
        # (This prevents crashes when a user edits their own profile later)
        user_id = self.instance.id if self.instance else None
        
        if CustomUser.objects.exclude(id=user_id).filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email address is already registered.")
            
        return value

    def get_full_name(self, obj):
        # Safely constructs full name or defaults to username
        f_name = getattr(obj, "first_name", "") or ""
        l_name = getattr(obj, "last_name", "") or ""
        combined = f"{f_name} {l_name}".strip()
        return combined if combined else obj.username

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def get_profile_picture(self, obj):
        photo = obj.photos.filter(is_profile_pic=True).first()
        return photo.image_url if photo else None

    def get_verification_status(self, obj):
        if obj.is_verified:
            return "verified"
        # If they are not verified, but have at least 1 ID proof, they are pending
        if obj.id_proofs.exists():
            return "pending"
        return "unverified"

    def get_album(self, obj):
        return [photo.image_url for photo in obj.photos.all()]


class ProfileViewLogSerializer(serializers.ModelSerializer):
    # This automatically picks up full_name now because it nests the updated UserSerializer!
    visitor_details = UserSerializer(source="visitor", read_only=True)

    class Meta:
        model = ProfileViewLog
        fields = ["id", "visitor_details", "timestamp"]
