from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("category_list", views.category_list, name="category_list"),
    path("<int:id>/category", views.category, name="category"),
    path("<int:id>/auction", views.auction, name="auction"),
]