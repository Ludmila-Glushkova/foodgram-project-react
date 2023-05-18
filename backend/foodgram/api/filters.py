from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import (
    ModelChoiceFilter,
    AllValuesMultipleFilter,
    BooleanFilter
)

from recipes.models import Recipe


User = get_user_model()


class RecipeFilter(FilterSet):
    author = ModelChoiceFilter(queryset=User.objects.all())
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = BooleanFilter(method='is_favorited_filter')
    is_in_shopping_cart = BooleanFilter(method='is_in_shopping_cart_filter')

    def is_favorited_filter(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(baskets__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
