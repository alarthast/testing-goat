from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from lists.models import Item, List


class ItemModelTest(TestCase):
    def test_default_text(self):
        item = Item()
        self.assertEqual(item.text, "")

    def test_saving_and_retrieving_items(self):
        mylist = List.objects.create()

        item = Item()
        item.list = mylist
        item.save()

        self.assertIn(item, mylist.item_set.all())

    def test_cannot_save_null_list_items(self):
        mylist = List.objects.create()
        item = Item(list=mylist, text=None)
        with self.assertRaises(IntegrityError):
            item.save()

    def test_cannot_save_empty_list_items(self):
        mylist = List.objects.create()
        item = Item(list=mylist, text="")
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_duplicate_items_are_invalid(self):
        mylist = List.objects.create()
        Item.objects.create(list=mylist, text="bla")
        with self.assertRaises(ValidationError):
            item = Item(list=mylist, text="bla")
            item.full_clean()

    def test_CAN_save_same_item_to_different_lists(self):
        list1 = List.objects.create()
        list2 = List.objects.create()
        Item.objects.create(list=list1, text="bla")
        item = Item(list=list2, text="bla")
        item.full_clean()  # should not raise

    def test_string_representation(self):
        item = Item(text="some text")
        self.assertEqual(str(item), "some text")

    def test_list_ordering(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text="i1")
        item2 = Item.objects.create(list=list1, text="item 2")
        item3 = Item.objects.create(list=list1, text="3")
        self.assertEqual(
            list(list1.item_set.all()),
            [item1, item2, item3],
        )


class ListModelTest(TestCase):
    def test_get_absolute_url(self):
        mylist = List.objects.create()
        self.assertEqual(mylist.get_absolute_url(), f"/lists/{mylist.id}/")
