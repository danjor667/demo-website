from django import forms


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=20, initial=1)


class FeedbackForm(forms.Form):
    CATEGORIES = [
        ("BUG", "Something is broken"),
        ("IMPROVEMENT", "Could be better"),
        ("FEATURE", "Feature request"),
        ("QUESTION", "Question"),
        ("GENERAL", "Other"),
    ]

    category = forms.ChoiceField(choices=CATEGORIES)
    message = forms.CharField(min_length=10, max_length=5000)
    name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=False)
    # Filled in by the page's script
    page_url = forms.URLField(max_length=500, required=False)
    browser = forms.CharField(max_length=300, required=False)
    viewport_width = forms.IntegerField(min_value=0, required=False)
    viewport_height = forms.IntegerField(min_value=0, required=False)
