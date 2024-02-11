from django.urls import path
from .views import register_view, login_view, logout_view

app_name = 'accounts'  # Add this line to specify the app namespace


urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
