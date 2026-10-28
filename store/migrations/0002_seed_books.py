from decimal import Decimal

from django.db import migrations

BOOKS = [
    ("A Brief History of Time", "Stephen Hawking", "science", "18.99",
     "From the Big Bang to black holes, a tour of how the universe works."),
    ("Clean Code", "Robert C. Martin", "programming", "37.50",
     "Practical advice on writing code that other people can read and change."),
    ("Cosmos", "Carl Sagan", "science", "16.00",
     "A journey through fifteen billion years of cosmic evolution."),
    ("Dune", "Frank Herbert", "fiction", "12.99",
     "A desert planet, a powerful family and the most valuable substance in the universe."),
    ("Eloquent JavaScript", "Marijn Haverbeke", "programming", "29.95",
     "A modern introduction to programming through JavaScript."),
    ("Fluent Python", "Luciano Ramalho", "programming", "54.00",
     "Clear, concise and effective programming with Python's best features."),
    ("Project Hail Mary", "Andy Weir", "fiction", "15.75",
     "A lone astronaut must save the earth from disaster."),
    ("Python Crash Course", "Eric Matthes", "programming", "32.40",
     "A hands-on, project-based introduction to programming."),
    ("The Pragmatic Programmer", "David Thomas & Andrew Hunt", "programming", "41.00",
     "Your journey to mastery, from journeyman to master."),
    ("The Gene", "Siddhartha Mukherjee", "science", "19.50",
     "An intimate history of the gene and what it means to be human."),
    ("The Name of the Wind", "Patrick Rothfuss", "fiction", "11.25",
     "The tale of Kvothe, from his childhood in a troupe of traveling players to legend."),
    ("Things Fall Apart", "Chinua Achebe", "fiction", "9.80",
     "The story of Okonkwo and the collapse of his world in colonial Nigeria."),
]


def add_books(apps, schema_editor):
    Book = apps.get_model("store", "Book")
    Book.objects.bulk_create(
        Book(title=title, author=author, category=category, price=Decimal(price), description=description)
        for title, author, category, price, description in BOOKS
    )


def remove_books(apps, schema_editor):
    apps.get_model("store", "Book").objects.filter(title__in=[book[0] for book in BOOKS]).delete()


class Migration(migrations.Migration):
    dependencies = [("store", "0001_initial")]

    operations = [migrations.RunPython(add_books, remove_books)]
