from django import forms
from django.core.exceptions import ValidationError

from lists.models import Item


DUPLICATE_ITEM_ERROR = "You've already got this in your list"
EMPTY_ITEM_ERROR = "You can't have an empty list item"


class ItemForm(forms.models.ModelForm):
    class Meta:
        model = Item
        fields = ("text",)
        widgets = {
            "text": forms.widgets.TextInput(
                attrs={
                    "placeholder": "Enter a to-do item",
                    "class": "form-control form-control-lg",
                    "aria-describedby": "id_text_feedback",
                }
            ),
        }
        error_messages = {"text": {"required": EMPTY_ITEM_ERROR}}

    def is_valid(self):
        # From https://stackoverflow.com/a/8256041
        result = super().is_valid()
        # loop on *all* fields if key '__all__' found else only on errors:
        for x in self.fields if "__all__" in self.errors else self.errors:
            attrs = self.fields[x].widget.attrs
            attrs.update({"class": attrs.get("class", "") + " is-invalid"})
        return result

    def save(self, for_list):
        self.instance.list = for_list
        return super().save()


class ExistingListItemForm(ItemForm):
    def __init__(self, for_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.list = for_list

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            e.error_dict = {"text": [DUPLICATE_ITEM_ERROR]}
            self._update_errors(e)

    def save(self):
        return forms.models.ModelForm.save(self)
