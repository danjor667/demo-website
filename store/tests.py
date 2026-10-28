import json
from decimal import Decimal
from unittest import mock

import requests
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Book


class BookListTests(TestCase):
    def test_lists_books(self):
        response = self.client.get(reverse("book_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h2>A Brief History of Time</h2>")

    def test_search_by_title(self):
        response = self.client.get(reverse("book_list"), {"q": "Dune"})
        self.assertContains(response, "<h2>Dune</h2>")
        self.assertNotContains(response, "<h2>Cosmos</h2>")

    def test_filter_by_category(self):
        response = self.client.get(reverse("book_list"), {"category": "fiction"})
        self.assertContains(response, "<h2>Dune</h2>")
        self.assertNotContains(response, "<h2>Clean Code</h2>")

    def test_invalid_page_falls_back_to_first(self):
        response = self.client.get(reverse("book_list"), {"page": "abc"})
        self.assertEqual(response.context["page"], 1)


class BookDetailTests(TestCase):
    def test_unknown_book_is_404(self):
        response = self.client.get(reverse("book_detail", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_add_to_cart(self):
        book = Book.objects.get(title="Dune")
        response = self.client.post(reverse("book_detail", args=[book.pk]), {"quantity": 1})
        self.assertRedirects(response, reverse("cart"))
        self.assertEqual(self.client.session["cart"], {str(book.pk): 1})

    def test_rejects_zero_quantity(self):
        book = Book.objects.get(title="Dune")
        response = self.client.post(reverse("book_detail", args=[book.pk]), {"quantity": 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get("cart", {}), {})


class CartTests(TestCase):
    def test_total_for_single_book(self):
        book = Book.objects.get(title="Dune")
        self.client.post(reverse("book_detail", args=[book.pk]), {"quantity": 1})
        response = self.client.get(reverse("cart"))
        self.assertEqual(response.context["total"], Decimal("12.99"))

    def test_invalid_discount_code(self):
        book = Book.objects.get(title="Dune")
        self.client.post(reverse("book_detail", args=[book.pk]), {"quantity": 1})
        self.client.post(reverse("cart"), {"action": "discount", "code": "FREEBOOKS"})
        self.assertNotIn("discount_code", self.client.session)

    def test_checkout_empties_cart(self):
        book = Book.objects.get(title="Dune")
        self.client.post(reverse("book_detail", args=[book.pk]), {"quantity": 1})
        response = self.client.post(reverse("checkout"))
        self.assertContains(response, "Thanks for your order")
        self.assertEqual(self.client.session["cart"], {})


@override_settings(FEEDBACK_API_URL="http://feedback.test/api/v1", FEEDBACK_PROJECT_ID="project-123")
class FeedbackTests(TestCase):
    valid = {
        "category": "BUG",
        "message": "The search box does not find anything.",
        "page_url": "http://localhost:8000/",
        "browser": "Test browser",
        "viewport_width": 390,
        "viewport_height": 844,
    }

    def test_rejects_short_message(self):
        response = self.client.post(reverse("submit_feedback"), {**self.valid, "message": "bad"})
        self.assertEqual(response.status_code, 400)

    @mock.patch("store.feedback.requests.post")
    def test_forwards_feedback_to_backend(self, post):
        post.return_value = mock.Mock(status_code=201)
        response = self.client.post(reverse("submit_feedback"), self.valid)

        self.assertEqual(response.json(), {"ok": True})
        url = post.call_args.args[0]
        payload = json.loads(post.call_args.kwargs["files"]["feedback"][1])
        self.assertEqual(url, "http://feedback.test/api/v1/feedback/submit")
        self.assertEqual(payload["projectId"], "project-123")
        self.assertEqual(payload["metadata"]["viewport"], {"width": 390, "height": 844})
        self.assertNotIn("user", payload)

    @mock.patch("store.feedback.requests.post", side_effect=requests.ConnectionError)
    def test_backend_down(self, post):
        response = self.client.post(reverse("submit_feedback"), self.valid)
        self.assertEqual(response.status_code, 502)
