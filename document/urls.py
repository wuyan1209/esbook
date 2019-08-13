from django.urls import path
from document import views

urlpatterns = [
    path('index/',views.index),
    path('mysql/',views.mysql_text),
    path('docs/', views.docs)
	path('mysql/',views.mysql_text),
	
]