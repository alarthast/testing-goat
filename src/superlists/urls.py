from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.views.generic.base import RedirectView

from lists import views as list_views


urlpatterns = [
    path("", list_views.home_page, name="home"),
    path("lists/", include("lists.urls")),
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("favicon/favicon.ico")),
    ),
]
