from django.db import models
from django.conf import settings


class Restaurant(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(max_length=255)
    currency = models.CharField(max_length=16, default='ETB')
    hero_message = models.TextField()
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='restaurants')

    def __str__(self):
        return self.name


class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=120)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['restaurant', 'name'], name='unique_category_name_per_restaurant'),
        ]

    def __str__(self):
        return self.name


class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables')
    number = models.PositiveIntegerField()
    label = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['number', 'id']

    def __str__(self):
        return self.label


class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=160)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='menu_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.URLField()
    available = models.BooleanField(default=True)
    spicy = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-featured', 'id']

    def __str__(self):
        return self.name
