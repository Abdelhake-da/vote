from django.urls import path
from . import views

urlpatterns = [
    path('', views.vote_page, name='vote_page'),  # URL for the vote page
    path('login/', views.login_view, name='login'),  # URL for login
    path('logout/', views.logout_view, name='logout'),  # URL for logout
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),  # URL for the admin dashboard
    path('statistics/', views.statistics_dashboard, name='statistics_dashboard'),  # URL for the statistics dashboard
    path('update-admin-info/', views.update_admin_info, name='update_admin_info'),  # URL for updating admin info
    path('upload-photo/', views.upload_photo, name='upload_photo'),  # URL for uploading photos
]
