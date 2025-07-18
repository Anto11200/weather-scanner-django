from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from .views import *

urlpatterns = [
    path('', views.weatherscanner, name=''),
    
    # path('search/', views.searchAjax),
    path('search/', SearchAjaxView.as_view()),
    
    # path('searched/<str:city>', views.searched),
    path('searched/<str:city>', SearchedView.as_view()),
    
    # path('searched/<str:city>/forecast/<str:service>', views.forecast),
    path('searched/<str:city>/forecast/<str:service>', ForecastView.as_view()),
    
    # path('searched/forecast/accuracy', views.accuracy),
    path('searched/forecast/accuracy', AccuracyView.as_view()),
    
    path('accuracy-info/', views.accuracyInfo),
    
    # urls per l'autenticazione 
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout')
]