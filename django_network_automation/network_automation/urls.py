from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name="home"),
    path('devices/', views.devices, name="devices"),
    path('config/', views.configuration, name="configur"),
    path('verify-result/', views.verify_config, name="verify-result"),
    path('log/', views.log, name="log"),
    # path('monitor/', views.monitor_network, name='monitor_network'),
    path('show/', views.show, name='show')
]
