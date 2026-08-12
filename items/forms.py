from django.forms import ModelForm
from .models import Item


class ItemForm(ModelForm):

    class Meta:

        model=Item

        fields=[
        'title',
        'item_type',
        'description',
        'location',
        'image',
        'contact'
        ]