from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    path('int-text/', views.interpret_text, name='get_huggingface_response'),
    path('register/', views.register_user, name='register_user'),
    path('login/', views.LoginView, name='Login_user'),
    
]
