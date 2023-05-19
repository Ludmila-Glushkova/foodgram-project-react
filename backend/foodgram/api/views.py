from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import AuthorOrAdminOrReadOnly, IsAuthenticatedOrAdmin
from recipes.models import (
    Basket,
    Favorites,
    Ingredient,
    IngredientRecipe,
    Recipe,
    Tag
)
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    TagSerializer
)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, permission_classes=(IsAuthenticatedOrAdmin,))
    def download_shopping_cart(self, request):
        if not Basket.objects.filter(
                user=request.user
        ).exists():
            return Response(
                {'errors': 'В корзине нет рецептов'},
                status=HTTP_400_BAD_REQUEST
            )
        ingredients = IngredientRecipe.objects.filter(
            recipes__baskets__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_list = ''
        for ingredient in ingredients:
            item = (f'* {ingredient["ingredient__name"]} '
                    f'({ingredient["ingredient__measurement_unit"]}) -- '
                    f'{ingredient["amount"]}\n\n'
                    )
            shopping_list += item
        return HttpResponse(shopping_list,
                            content_type='text/plain;charset=UTF-8'
                            )

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticatedOrAdmin,)
            )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        basket_filter = Basket.objects.filter(
            user=request.user,
            recipe=recipe
        )
        if request.method == 'POST':
            serializer = ShortRecipeSerializer(recipe)
            if basket_filter.exists():
                return Response(
                    {'errors': 'Рецепт уже есть в списке покупок'},
                    status=HTTP_400_BAD_REQUEST
                )
            Basket.objects.create(
                user=request.user,
                recipe=recipe
            )
            return Response(serializer.data, status=HTTP_201_CREATED)
        if not basket_filter.exists():
            return Response(
                {'errors': 'Рецепта нет в корзине'},
                status=HTTP_400_BAD_REQUEST
            )
        basket_filter.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticatedOrAdmin,)
            )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        favorites_filter = Favorites.objects.filter(
                user=request.user,
                recipe=recipe
            )
        if request.method == 'POST':
            serializer = ShortRecipeSerializer(recipe)
            if favorites_filter.exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен в избранное'},
                    status=HTTP_400_BAD_REQUEST
                )
            Favorites.objects.create(
                user=request.user,
                recipe=recipe
            )
            return Response(serializer.data, status=HTTP_201_CREATED)
        if not favorites_filter.exists():
            return Response(
                {'errors': 'Рецепта нет в избранном'},
                status=HTTP_400_BAD_REQUEST
            )
        favorites_filter.delete()
        return Response(status=HTTP_204_NO_CONTENT)
