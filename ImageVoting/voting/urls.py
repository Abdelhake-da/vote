from django.urls import path
from . import views

urlpatterns = [
    path('', views.vote_page, name='vote_page'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
