from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('', views.index, name='about'),
    path('', views.index, name='price'),
    path('Terminos&Condiciones/', views.TermsAndCondition, name='termsCondition'),
]