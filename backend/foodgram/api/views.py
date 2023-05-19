from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import filters, mixins, status, viewsets

from djoser.conf import settings
from djoser.views import UserViewSet

from api.filters import RecipeFilters
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CustomUserSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeSimplifiedSerializer,
                             RecipeWriteSerializer, RegistrationSerializer,
                             SubscribeSerializer, SubscriptionsSerializer,
                             TagSerializer)
from foodgram.settings import FILE_NAME
from recipes.models import (Favorites, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Follow, User


class CustomUserViewSet(UserViewSet):
    """
    Кастомизированный вьюсет.
    Регистрация, получение списка пользователей/ отдельного пользователя,
    своего профиля, перечня своих подписок.
    Подписка на пользователей. Чтение и удаление.
    """

    permission_classes = (AllowAny,)
    http_method_names = ['get', 'post', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CustomUserSerializer
        elif self.action == "set_password":
            return settings.SERIALIZERS.set_password
        elif self.action == "me":
            return settings.SERIALIZERS.current_user
        return RegistrationSerializer

    @action(methods=['get'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, **kwargs)

    @action(methods=['get'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            pagination_class=CustomPagination)
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(page,
                                             many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('id'))
        if request.method == 'POST':
            serializer = SubscribeSerializer(author,
                                             data=request.data,
                                             context={"request": request})
            serializer.is_valid(raise_exception=True)
            if request.user == author:
                return Response('Нельзя подписаться на самого себя.',
                                status=status.HTTP_400_BAD_REQUEST)
            if not Follow.objects.filter(user=request.user, author=author):
                Follow.objects.create(user=request.user, author=author)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response('Вы уже подписаны на этого пользователя.',
                            status=status.HTTP_400_BAD_REQUEST)
        is_in_subscriptions = Follow.objects.filter(
            user=request.user, author=author)
        if is_in_subscriptions:
            is_in_subscriptions.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Вы не подписаны на этого пользователя.',
                        status=status.HTTP_400_BAD_REQUEST)


class IngredientListViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение отдельного ингредиента/ списка ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение отдельного тега/ списка тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                    mixins.ListModelMixin, mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Кастомизированный вьюсет из миксинов.
    Получение списка рецептов/ отдельного рецепта.
    Создание, редактирование, удаление своего рецепта.
    Добавление рецептов в избранное. Чтение и удаление.
    Добавление рецептов в корзину. Чтение и удаление.
    Формирование и скачивание списка покупок из корзины.
    """

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilters
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthorOrReadOnly,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = RecipeSimplifiedSerializer(recipe,
                                                    data=request.data,
                                                    context={
                                                        "request": request})
            serializer.is_valid(raise_exception=True)
            if not Favorites.objects.filter(user=request.user,
                                            recipe=recipe).exists():
                Favorites.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response('Рецепт уже добавлен в избранное.',
                            status=status.HTTP_400_BAD_REQUEST)

        is_in_favorites = Favorites.objects.filter(
            user=request.user, recipe=recipe)
        if is_in_favorites:
            is_in_favorites.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('В избранном пусто, нечего удалять.',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthorOrReadOnly,),
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = RecipeSimplifiedSerializer(
                recipe, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not ShoppingCart.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response('Рецепт уже добавлен в корзину.',
                            status=status.HTTP_400_BAD_REQUEST)

        is_in_shopping_cart = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe)
        if is_in_shopping_cart:
            is_in_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Корзина пуста, нечего удалять.',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'],
            detail=False,
            permission_classes=(IsAuthenticated, IsAuthorOrReadOnly,))
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (IngredientRecipe.objects
                       .filter(recipe__cart_recipe__user=request.user)
                       .values('ingredient')
                       .annotate(total_amount=Sum('amount'))
                       .values_list('ingredient__name', 'total_amount',
                                    'ingredient__measurement_unit'))
        file_list = []
        [file_list.append(
            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients]
        file = HttpResponse('Cписок покупок:\n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = (f'attachment; filename={FILE_NAME}')
        return file
