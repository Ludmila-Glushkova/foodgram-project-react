from re import match

from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import (
    SerializerMethodField,
    ValidationError,
    ModelSerializer
)
from rest_framework.status import HTTP_400_BAD_REQUEST

import api.serializers
from .models import Follow


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        write_only_fields = ('password',)

    def validate_username(self, value):
        if not match(r'[\w.@+\-]+', value):
            raise ValidationError('Некорректный логин')
        return value


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user,
            author=obj
        ).exists()


class FollowSerializer(ModelSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = api.serializers.ShortRecipeSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user,
            author=obj
        ).exists()

    def validate(self, data):
        user = self.context.get('request').user
        author = self.instance
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на свой аккаунт',
                code=HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(
            user=user,
            author=author
        ).exists():
            raise ValidationError(
                detail='Нельзя повторно подписаться на пользователя',
                code=HTTP_400_BAD_REQUEST
            )
        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        author = validated_data.get('author')
        return Follow.objects.create(user=user, author=author)
