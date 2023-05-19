from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CustomUserViewSet, IngredientListViewSet,
                       RecipeViewSet, TagViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientListViewSet,
                basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('users', CustomUserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls.authtoken',))
]
