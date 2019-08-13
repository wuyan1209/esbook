from django.urls import path
from document import views

urlpatterns = [
    path('index/',views.index),
    path('docs/', views.docs)
]