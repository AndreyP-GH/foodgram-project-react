from django.core.validators import MinValueValidator
from django.db import models

from recipes.validators import validate_not_empty
from users.models import User

LEN_LIMIT = 20


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        validators=[validate_not_empty])
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        validators=[validate_not_empty])

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name[:LEN_LIMIT]}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        verbose_name='Название тега',
        unique=True,
        max_length=200,
        validators=[validate_not_empty])
    color = models.CharField(
        verbose_name='Цветовой HEX-код тега',
        unique=True,
        max_length=7,
        validators=[validate_not_empty])
    slug = models.SlugField(
        verbose_name='Уникальный слаг тега',
        unique=True,
        max_length=200)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:LEN_LIMIT]


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
        blank=False)
    name = models.CharField(
        verbose_name='Название рецепта',
        unique=True,
        max_length=200,
        blank=False)
    text = models.TextField(
        verbose_name='Текстовое описание рецепта',
        help_text='Добавить описание рецепта',
        blank=False)
    image = models.ImageField(
        verbose_name='Картинка рецепта',
        help_text='Здесь нужно добавить картинку',
        upload_to='recipes/%Y/%m/%d/',
        blank=False)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
        related_name='recipes',
        blank=False)
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Тег(и) блюда',
        blank=False,
        related_name='recipes')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин.',
        validators=[MinValueValidator(1)])
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации рецепта',
        auto_now_add=True,
        db_index=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:LEN_LIMIT]


class IngredientRecipe(models.Model):
    """Связь моделей ингредиентов и рецептов. Многие ко многим."""

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredients')
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipes')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredients'),
        ]

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'[:LEN_LIMIT]


class TagRecipe(models.Model):
    """Связь моделей тегов и рецептов. Многие ко многим."""

    tag = models.ForeignKey(
        Tag,
        null=True,
        on_delete=models.SET_NULL)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'


class Favorites(models.Model):
    """Модель избранных рецептов пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'),
        ]

    def __str__(self):
        return f'{self.user}: избранные рецепты'[:LEN_LIMIT]


class ShoppingCart(models.Model):
    """Модель списка покупок пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_user')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart_recipe')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoppingcart'),
        ]

    def __str__(self):
        return f'{self.user}: список покупок'[:LEN_LIMIT]
