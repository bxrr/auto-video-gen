from django.urls import path

from . import views

app_name = "generate"
urlpatterns = [
    path("", views.index, name="index"),
    path("loading/", views.loading, name="loading"),
    path("generate/", views.generate, name="generate"),
]