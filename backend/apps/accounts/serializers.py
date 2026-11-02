from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .constants import Role

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Add user info to JWT payload."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["full_name"] = user.get_full_name()
        token["role"] = user.role
        token["role_level"] = user.role_level
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data["user"] = {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.get_full_name(),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "role_label": user.get_role_display(),
            "role_level": user.role_level,
            "avatar": user.avatar.url if user.avatar else None,
        }
        return data


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_label = serializers.CharField(source="get_role_display", read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "full_name",
            "role", "role_label", "phone", "avatar_url",
            "is_active", "date_joined", "cell_group", "member",
        ]
        read_only_fields = ["id", "date_joined"]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email", "first_name", "last_name", "role",
            "phone", "password", "confirm_password", "cell_group",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError({"confirm_new_password": "Passwords do not match."})
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Self-service profile update (non-sensitive fields only)."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "avatar"]
