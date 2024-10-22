from django.urls import path
from . import views

urlpatterns = [
    # OPENAI URLS
    path('routine/loadinfo', views.interpret_Routine, name='get_huggingface_routineInfo'),
    path('camera/scannedInfo', views.interpret_MachineInfo, name='get_huggingface_scannedInfo'),

    # AUTH PAGE
    path('register/', views.register_user, name='register_user'),
    path('login/', views.LoginView, name='Login_user'),

    #MODIFY MODELS
    path('edit-profile/', views.UserEditarMultiParser.as_view(), name='edit-profile'),
    path('getuser/<int:id>/', views.get_user, name='get-user'),
    path('feedback/create/', views.FeedbackCreateView.as_view(), name='feedback-create'),

    # RESET PASSWORD

    path('request_password_recovery/', views.RequestPasswordResetView.as_view(), name='Request_Recovery'),
    path('reset_password/', views.PasswordResetConfirmView.as_view(), name='Reset_password'),
]
