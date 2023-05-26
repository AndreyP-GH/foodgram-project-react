import base64

from django.core.files.base import ContentFile
from djoser.serializers import (SetPasswordSerializer, UserCreateSerializer,
                                UserSerializer)
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from recipes.models import (Favorites, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    """Конвертация изображения."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RegistrationSerializer(UserCreateSerializer):
    """Регистрация пользователя. Запись."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'password',
                  'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }

    def validate(self, data):
        username = data.get('username')
        if username.lower() == 'me':
            raise ValidationError(
                'Имя пользователя me недопустимо. Используйте другое имя.')
        return data


class CustomUserSerializer(UserSerializer):
    """Данные пользователя. Чтение."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(user=user, author=obj).exists()
        return False


class CurrentUserSerializer(CustomUserSerializer):
    """Текущий пользователь для Djoser."""

    pass


class PasswordChangeSerializer(SetPasswordSerializer):
    """Смена пароля для Djoser."""

    pass


class RecipeSimplifiedSerializer(serializers.ModelSerializer):
    """Упрощенный рецепт без ингредиентов для подписок автора. Чтение."""

    name = serializers.ReadOnlyField()
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Список подписок/ авторов пользователя. Чтение."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(user=user, author=obj).exists()
        return False

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        serializer = RecipeSimplifiedSerializer(recipes,
                                                many=True,
                                                read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    """Подписка на автора. Запись и удаление."""

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        user = data['user']
        author = data['author']
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Отдельный ингредиент/ список ингредиентов. Чтение."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Отдельный тег/ спискок тегов. Чтение."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientRecipeReadSerializer(serializers.ModelSerializer):
    """Cвязь ингредиента и рецепта для чтения рецепта. Чтение."""

    id = serializers.PrimaryKeyRelatedField(read_only=True,
                                            source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    """Связь ингредиента и рецепта для записи рецепта. Запись."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Рецепт. Чтение."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeReadSerializer(many=True,
                                                 read_only=True,
                                                 source='recipes')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Favorites.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Рецепт. Запись, редактирование и удаление."""

    id = serializers.ReadOnlyField()
    ingredients = IngredientRecipeWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author')

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        if not data.get('ingredients'):
            raise serializers.ValidationError(
                'Нельзя создать рецепт без ингредиентов.')
        if not data.get('tags'):
            raise serializers.ValidationError(
                'Нельзя создать рецепт без тегов.')
        if len(ingredients) != len(set([item['id'] for item in ingredients])):
            raise serializers.ValidationError(
                'Этот ингредиент уже добавлен.')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Этот тег уже добавлен.')
        return data

    def ingredient_tag_create(self, recipe, ingredients, tags):
        recipe.tags.set(tags)
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']) for ingredient in ingredients]
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=self.context.get('request').user,
                                       **validated_data)
        self.ingredient_tag_create(recipe, ingredients, tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        IngredientRecipe.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        self.ingredient_tag_create(instance, ingredients, tags)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data
