from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=200,
        unique=True,
        help_text='Необходимо указать название тега'
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        null=True,
        unique=True,
        help_text='Необходимо указать цвет тега'
    )
    slug = models.SlugField(
        'Слаг',
        max_length=200,
        unique=True,
        null=True,
        help_text='Необходимо указать слаг тега'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=200,
        unique=True,
        help_text='Необходимо указать название ингредиента'
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
        help_text='Необходимо указать единицу измерения ингредиента'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент, который связан с рецептом'
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=(MinValueValidator(1),)
    )

    class Meta:
        verbose_name = 'Ингредиент с количеством'
        verbose_name_plural = 'Ингредиенты с количеством'
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'amount'),
                name='Ингредиент и количество должны быть с уникальной связью'
            )
        ]

    def __str__(self):
        return f'Ингредиент {self.ingredient} в количестве {self.amount}'


class Recipe(models.Model):
    name = models.CharField(
        'Название рецепта',
        max_length=200,
        help_text='Необходимо указать название рецепта'
    )
    text = models.TextField(
        'Описание рецепта',
        help_text='Необходимо указать описание рецепта'
    )
    image = models.ImageField(
        'Картинка рецепта',
        upload_to='recipes/images/',
        help_text='Необходимо прикрепить картинку рецепта'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        IngredientRecipe,
        verbose_name='Ингредиенты',
        related_name='recipes'
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        validators=(MinValueValidator(1),),
        help_text='Необходимо указать время приготовления рецепта'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE,
        verbose_name='Пользователь, который добавляет в избранное продукты'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorites',
        on_delete=models.CASCADE,
        verbose_name='Рецепт в избранном'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='Нельзя повторно добавить рецепт в избранное'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил рецепт {self.recipe} в избранное'


class Basket(models.Model):
    user = models.ForeignKey(
        User,
        related_name='baskets',
        on_delete=models.CASCADE,
        verbose_name='Пользователь, который добавляет рецепты в корзину'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='baskets',
        on_delete=models.CASCADE,
        verbose_name='Рецепты в корзине'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='Нельзя повторно добавить рецепт в корзину'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил рецепт {self.recipe} в корзину'
