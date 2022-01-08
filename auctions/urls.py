from django.urls import path

from . import views

app_name ="auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("alllistings", views.alllistings, name="alllistings"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listings/<str:listing_title>", views.listing, name="title"),
    path("create", views.create, name="create_listing"),
    path("userlisting", views.userlisting, name="user_listing"),
    path("deletelisting/<listing_id>", views.deletelisting, name="deletelisting"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("delete/<watchlist_id>",views.delete,name='delete'),
    path("category",views.category,name='category'),
    path("fashion",views.fashion,name='fashion'),
    path("toys",views.toys,name='toys'),
    path("electronics",views.electronics,name='electronics'),
    path("home",views.home,name='home'),
    path("uncategorized",views.uncategorized,name='uncategorized'),
    path("error", views.error, name="error"),

]
