from decimal import Decimal

from .models import Book

# Code -> percent off the order total.
DISCOUNT_CODES = {"SAVE10": 10}


class Cart:
    """A shopping cart kept in the session as {book id: quantity}."""

    def __init__(self, request):
        self.session = request.session
        self.items = self.session.setdefault("cart", {})

    def add(self, book, quantity=1):
        key = str(book.id)
        self.items[key] = self.items.get(key, 0) + quantity
        self._save()

    def remove(self, book_id):
        self.items.pop(str(book_id), None)
        self._save()

    def clear(self):
        self.items.clear()
        self.session.pop("discount_code", None)
        self._save()

    def count(self):
        return sum(self.items.values())

    def lines(self):
        books = Book.objects.filter(id__in=self.items.keys())
        return [
            {
                "book": book,
                "quantity": self.items[str(book.id)],
                "line_total": book.price * self.items[str(book.id)],
            }
            for book in books
        ]

    def total(self):
        return sum((line["book"].price for line in self.lines()), Decimal("0"))

    def _save(self):
        self.session.modified = True


def apply_discount(total, code):
    """Return (discounted total, whether the code was valid)."""
    percent = DISCOUNT_CODES.get(code.strip().upper())
    if percent is None:
        return total, False
    return max(total - Decimal(percent), Decimal("0")), True
