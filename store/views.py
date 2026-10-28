import logging

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import Cart, apply_discount
from .feedback import FeedbackNotSent, send_feedback
from .forms import AddToCartForm, FeedbackForm
from .models import Book

logger = logging.getLogger(__name__)

BOOKS_PER_PAGE = 5


def book_list(request):
    books = Book.objects.all()
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")

    if query:
        books = books.filter(title__icontains=query)
    if category:
        books = books.filter(category=category)

    try:
        page = max(int(request.GET.get("page", 1)), 1)
    except ValueError:
        page = 1
    total_pages = max(books.count() // BOOKS_PER_PAGE, 1)
    page = min(page, total_pages)
    start = (page - 1) * BOOKS_PER_PAGE

    return render(request, "store/book_list.html", {
        "books": books[start:start + BOOKS_PER_PAGE],
        "query": query,
        "category": category,
        "categories": Book.Category.choices,
        "page": page,
        "total_pages": total_pages,
        "pages": range(1, total_pages + 1),
    })


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = AddToCartForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        Cart(request).add(book, form.cleaned_data["quantity"])
        messages.success(request, f"Added {book.title} to your cart.")
        return redirect("cart")
    return render(request, "store/book_detail.html", {"book": book, "form": form})


def cart_view(request):
    cart = Cart(request)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "remove":
            cart.remove(request.POST.get("book_id"))
        elif action == "discount":
            code = request.POST.get("code", "")
            if apply_discount(cart.total(), code)[1]:
                request.session["discount_code"] = code.strip().upper()
                messages.success(request, "Discount applied.")
            else:
                messages.error(request, "That discount code isn't valid.")
        return redirect("cart")

    subtotal = cart.total()
    code = request.session.get("discount_code")
    total = apply_discount(subtotal, code)[0] if code else subtotal
    return render(request, "store/cart.html", {
        "lines": cart.lines(),
        "subtotal": subtotal,
        "discount_code": code,
        "total": total,
    })


@require_POST
def checkout(request):
    cart = Cart(request)
    if not cart.count():
        return redirect("cart")
    subtotal = cart.total()
    code = request.session.get("discount_code")
    total = apply_discount(subtotal, code)[0] if code else subtotal
    cart.clear()
    return render(request, "store/order_confirmed.html", {"total": total})


@require_POST
def submit_feedback(request):
    form = FeedbackForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)
    try:
        send_feedback(form.cleaned_data)
    except FeedbackNotSent:
        logger.exception("Could not send feedback")
        return JsonResponse({"ok": False, "error": "We couldn't send your feedback. Please try again later."}, status=502)
    return JsonResponse({"ok": True})
