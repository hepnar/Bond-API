#!python3
# -*- codding: utf-8 -*-

from django.urls import path
from bonds_api.bond_views import BondListApiView
from bonds_api.bond_views import BondDetailApiView
from bonds_api.bond_views import UserDetailApiView

urlpatterns = [
    path("api", BondListApiView.as_view(), name="bond-list"),
    path("detail/<str:bond_id>/api", BondDetailApiView.as_view(),
         name="bond-detail"),
    path("user/<int:user_id>/api", UserDetailApiView.as_view(),
         name="bond-user-detail"),
]
