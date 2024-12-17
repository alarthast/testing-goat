from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from lists.models import Item, List


# Create your views here.
def home_page(request):
    return render(request, "home.html")


def new_list(request):
    mylist = List.objects.create()
    item = Item.objects.create(text=request.POST["item_text"], list=mylist)
    try:
        item.full_clean()
        item.save()
    except ValidationError:
        mylist.delete()
        error = "You can't have an empty list item"
        return render(request, "home.html", {"error": error})
    return redirect(f"/lists/{mylist.id}/")


def view_list(request, list_id):
    our_list = List.objects.get(id=list_id)
    if request.method == "POST":
        Item.objects.create(text=request.POST["item_text"], list=our_list)
        return redirect(f"/lists/{our_list.id}/")
    return render(request, "list.html", {"list": our_list})
