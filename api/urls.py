from django.urls import path, include

urlpatterns = [
    path('v1/', include('api.v1.urls')),
    # Future versions can be added like:
    # path('v2/', include('api.v2.urls')),
]