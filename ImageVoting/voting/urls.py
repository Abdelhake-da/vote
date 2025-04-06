from django.urls import path
from . import views

urlpatterns = [
    path('', views.vote_page, name='vote_page'),  # URL for the vote page
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),  # URL for the admin dashboard
    path('update-admin-info/', views.update_admin_info, name='update_admin_info'),  # URL for updating admin info
]
