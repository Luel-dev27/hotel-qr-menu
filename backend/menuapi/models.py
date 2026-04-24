from django.db import models


class Restaurant(models.Model):
    name = models.CharField(max_length=120)
    tagline = models.CharField(max_length=255)
    currency = models.CharField(max_length=16, default='ETB')
    hero_message = models.TextField()

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class Table(models.Model):
    number = models.PositiveIntegerField()
    label = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['number', 'id']

    def __str__(self):
        return self.label


class MenuItem(models.Model):
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
