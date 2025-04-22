from django.urls import path

from . import views
from .views import register, user_login

urlpatterns = [
    path('<int:user_id>', views.profile, name='profile'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),

]