from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    #path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('record/<int:pk>', views.customer_record, name='record'),
    path('delete_record/<int:pk>', views.delete_record, name='delete_record'),
    path('add_record/', views.add_record, name='add_record'),
    path('update_record/<int:pk>', views.update_record, name='update_record'),
    path('ai_dashboard/', views.ai_dashboard, name='ai_dashboard'),
    path('ai_engagement/', views.ai_engagement, name='ai_engagement'),
    path('smart_workflows/', views.smart_workflows, name='smart_workflows'),
    path('analytics_dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('send_message/', views.send_message, name='send_message'),
]
