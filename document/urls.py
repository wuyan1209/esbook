from django.urls import path
from document import views

urlpatterns = [
    path('index/', views.index),
    path('RTFdocs/', views.RTFdocs),
    path('mysql/', views.mysql_text),
    path('addTeam/', views.addTeam),
    path('select/', views.select),
    path('saveDocTest/', views.RTFdocs_save),
    path('docNameExist/', views.docNameExist)
]
