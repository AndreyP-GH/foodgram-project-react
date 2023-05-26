from django.contrib import admin

from recipes.models import (Favorites, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag, TagRecipe)


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    """Отображение избранных рецептов в админ-панели."""

    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user',)
    search_fields = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Отображение ингредиентов в админ-панели."""

    list_display = ('pk', 'name', 'measurement_unit',)
    list_editable = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    empty_value_display = '-пусто-'
    inlines = [IngredientRecipeInline]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Отображение рецептов в админ-панели."""

    list_display = ('pk', 'author', 'pub_date', 'name', 'get_ingredients',
                    'text', 'image', 'cooking_time', 'count_favorites',)
    list_editable = ('name', 'text', 'image', 'cooking_time',)
    search_fields = ('author__username', 'name', 'tags__name',)
    list_filter = ('author', 'tags', 'name',)
    empty_value_display = '-пусто-'
    inlines = [IngredientRecipeInline, TagRecipeInline]

    def count_favorites(self, obj):
        return Favorites.objects.filter(recipe=obj).count()

    def get_ingredients(self, obj):
        return ", ".join([i.name for i in obj.ingredients.all()])


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Отображение списка покупок в админ-панели."""

    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user',)
    search_fields = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Отображение тегов в админ-панели."""

    list_display = ('pk', 'name', 'color', 'slug',)
    list_editable = ('name', 'color', 'slug',)
    search_fields = ('name', 'slug',)
    empty_value_display = '-пусто-'
    inlines = [TagRecipeInline]
