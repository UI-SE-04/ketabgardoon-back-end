from django.urls import path

from . import views

urlpatterns = [
    path('<id:int>', views.book, name='book'),
]