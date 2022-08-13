from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiev_watched", views.wiev_watched,  name="wiev_watched"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("category_list", views.category_list, name="category_list"),
    path("<int:id>/watch_auction", views.watch_auction, name="watch_auction"),
    path("<int:id>/category", views.category, name="category"),
    path("<int:id>/auction", views.auction, name="auction"),
    path("<int:id>/auction_comment", views.auction_comment, name="auction_comment"),
    path("<int:id>/auction_bid", views.auction_bid, name="auction_bid"),
    path("<int:id>/auction_close", views.auction_close, name="auction_close"),
    path("create_auction", views.create_auction, name="create_auction")
]