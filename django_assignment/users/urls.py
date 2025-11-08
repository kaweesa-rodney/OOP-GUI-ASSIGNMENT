from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('add_user/', views.register_user, name='register_user'),          # Create new user
    #path('<int:pk>/update/', views.update_user, name='update_user'), # Update user by ID
    #path('<int:pk>/delete/', views.delete_user, name='delete_user'),
    path('users/', views.users, name='users'),
    path('dash/', views.dash, name="dash"),
    path('logout/', views.logout_view, name='logout_view'),
    path('change_password/', views.change_password, name="change_password"),
    path('disable_user/<int:id>', views.disable_user, name='disable_user'),
    path('activate_user/<int:id>', views.activate_user, name='activate_user'),
]