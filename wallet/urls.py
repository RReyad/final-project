from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    #API routes
    path("add_to_wallet",views.add_to_wallet, name="add_to_wallet"),
    path("transfer_to_wallet", views.transfer_to_wallet, name="transfer_to_wallet"),
    path("transactions", views.transactions, name = "transactions"),
    path("balance", views.balance, name="balance"),

]
