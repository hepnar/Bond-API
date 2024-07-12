#!python3
# -*- codding: utf-8 -*-

from django.urls import re_path
from django.urls import path
from django.urls import include
from bonds_api import bond_urls
from bonds_api.bond_views import schema_view

urlpatterns = [
]

urlpatterns = [
    path("api-auth/", include("rest_framework.urls")),
    path("bonds/", include(bond_urls)),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
