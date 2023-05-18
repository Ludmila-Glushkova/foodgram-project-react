from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import (
    Basket,
    Favorites,
    Ingredient,
    IngredientRecipe,
    Recipe,
    Tag
)


class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author', 'count_favorites')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)

    def count_favorites(self, obj):
        return obj.favorites.count()


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorites)
admin.site.register(Basket)
admin.site.register(IngredientRecipe)
