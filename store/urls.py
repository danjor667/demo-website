from django.urls import path

from . import views

urlpatterns = [
    path("", views.book_list, name="book_list"),
    path("books/<int:pk>/", views.book_detail, name="book_detail"),
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("feedback/", views.submit_feedback, name="submit_feedback"),
]
