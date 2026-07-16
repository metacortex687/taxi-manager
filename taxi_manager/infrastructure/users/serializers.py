from djoser.serializers import UserSerializer

from taxi_manager.infrastructure.users.models import User


class CurrentUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            "email",
            "id",
            "username",
            "uuid",
        )