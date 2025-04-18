from django.urls import path
from . import views


urlpatterns = [
    # GET    /api/v1/nationalities/         → nationality_list
    path('', views.nationality_list, name='nat-list'),

    # POST   /api/v1/nationalities/create/  → nationality_create
    path('create/', views.nationality_create, name='nat-create'),

    # GET    /api/v1/nationalities/<pk>/    → nationality_detail
    path('<int:pk>/', views.nationality_detail, name='nat-detail'),

    # PUT/PATCH /api/v1/nationalities/<pk>/update/
    path('<int:pk>/update/', views.nationality_update, name='nat-update'),

    # DELETE   /api/v1/nationalities/<pk>/delete/
    path('<int:pk>/delete/', views.nationality_delete, name='nat-delete'),
]