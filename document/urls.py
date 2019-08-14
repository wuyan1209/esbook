from django.urls import path
from document import views

urlpatterns = [
    path('index/',views.index),
    path('RTFdocs/', views.RTFdocs),
    path('mysql/',views.mysql_text),
    path('addTeam/', views.addTeam),

    path('select/', views.select),
]