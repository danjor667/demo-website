from django.db import models


class Book(models.Model):
    class Category(models.TextChoices):
        PROGRAMMING = "programming", "Programming"
        FICTION = "fiction", "Fiction"
        SCIENCE = "science", "Science"

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=Category.choices)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
