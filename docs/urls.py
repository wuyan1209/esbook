from django.urls import path
from . import models,views

urlpatterns = [
    path('getDocsSaveState/', views.getDocsSaveState)
]