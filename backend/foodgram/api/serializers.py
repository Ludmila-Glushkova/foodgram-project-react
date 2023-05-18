from base64 import b64decode

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework.serializers import (
    CharField,
    ImageField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError
)
from rest_framework.status import HTTP_400_BAD_REQUEST

from recipes.models import (
    Basket,
    Favorites,
    Ingredient,
    IngredientRecipe,
    Recipe,
    Tag
)
from users.serializers import CustomUserSerializer


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientRecipeSerializer(ModelSerializer):
    id = CharField(source='ingredient.id')
    name = CharField(source='ingredient.name')
    measurement_unit = CharField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class ShortRecipeSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True
    )
    author = CustomUserSerializer(read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def add_ingredients(self, instance, ingredients):
        for ingredient in ingredients:
            ing, _ = IngredientRecipe.objects.get_or_create(
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
            instance.ingredients.add(ing)
        return instance

    def create(self, validated_data):
        tags = self.validate_tags(self.initial_data.get('tags'))
        ingredients = self.validate_ingredients(
            self.initial_data.get('ingredients')
        )
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        return self.add_ingredients(recipe, ingredients)

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        tags = self.validate_tags(self.initial_data.get('tags'))
        ingredients = self.validate_ingredients(
            self.initial_data.get('ingredients')
        )
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        instance = self.add_ingredients(instance, ingredients)
        instance.save()
        return instance

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorites.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Basket.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise ValidationError(
                {'ingredients': ('В рецепте нужен хотя бы 1 ингредиент')},
                code=HTTP_400_BAD_REQUEST
            )
        ingredient_list = []
        for ingredient in value:
            current_ingredient = get_object_or_404(
                Ingredient,
                pk=ingredient.get('id')
            )
            if current_ingredient in ingredient_list:
                raise ValidationError(
                    {'ingredients': ('Все ингредиенты должны быть уникальны')},
                    code=HTTP_400_BAD_REQUEST
                )
            if int(ingredient.get('amount')) < 1:
                raise ValidationError(
                    {'ingredients': ('Количество должно быть больше 0')},
                    code=HTTP_400_BAD_REQUEST
                )
            ingredient_list.append(current_ingredient)
        return value

    def validate_tags(self, value):
        tags_set = set(value)
        if len(tags_set) != len(value):
            raise ValidationError(
                {'tags': 'Все теги должны быть уникальны'},
                code=HTTP_400_BAD_REQUEST
            )
        return value
