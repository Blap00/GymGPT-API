from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    path('int-text/', views.interpret_text, name='get_huggingface_response'),
    path('register/', views.register_user, name='register_user'),
    path('login/', views.LoginView, name='Login_user'),
    path('edit-profile/', views.UserEditView.as_view(), name='edit-profile'),
    path('getuser/<int:id>/', views.get_user, name='get-user'),
    path('feedback/create/', views.FeedbackCreateView.as_view(), name='feedback-create'),
    path('generate_routine/<int:usuarioID>', views.generate_routine, name='generate-routine')
]
