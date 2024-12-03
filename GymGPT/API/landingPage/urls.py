from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.aboutUs, name='about'),
    path('Terminos&Condiciones/', views.TermsAndCondition, name='termsCondition'),
]