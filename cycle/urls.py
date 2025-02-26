from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.start, name='start'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    # path('kyc/', views.kyc_view, name='kyc'),
    path('home/', views.home_view, name='home'),
   
    path("home/health/", views.health, name="health"),
    path('home/mumbai_map/', views.offline, name='offline'),
   
    path('home/area_flag/', views.area_flag, name='area_flag'),
    path('home/anomoly/', views.anomoly, name='anomoly'),
    path('home/profile/', views.ride, name='ride'),

 
    
    path('api/send-emergency-alert/', views.send_emergency_alert, name='send_emergency_alert'),
    
   

   
    path("send-sos/", views.send_sos, name="send_sos"),

    path('api/send-emergency-alert/', views.send_emergency_alert, name='send_emergency_alert'),

   

  
]