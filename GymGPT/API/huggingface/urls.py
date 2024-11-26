from django.urls import path
from . import views

urlpatterns = [
    # OPENAI URLS
    path('routine/loadinfo/', views.interpret_Routine, name='get_huggingface_routineInfo'),
    path('camera/scannedInfo', views.interpret_MachineInfo, name='get_huggingface_scannedInfo'),

    # AUTH PAGE
    path('register/', views.register_user, name='register_user'),
    path('login/', views.LoginView, name='Login_user'),

    #MODIFY MODELS
    path('edit-profile/', views.UserEditarMultiParser.as_view(), name='edit-profile'),
    path('feedback/create/', views.FeedbackCreateView.as_view(), name='feedback-create'),

    # Get DATA USER
    path('getuser/<int:id>/', views.get_user, name='get-user'),
    path('camera/infoBy/<int:id>',views.getMachineInfo, name='Get_MachineInfo_byUser'),
    path('routine/infoBy/<int:id>/',views.getRoutineInfo, name='Get_RoutineInfo_byUser'),
    path('routine/nameBy/<int:id>', views.getLastRoutineUser, name='Get_last_routine_USER'),
    path('routine/infoBy/<int:id>/all',views.getRoutineInfoAll, name='Get_RoutineInfo_byUserAll'),
    
    # RESET PASSWORD
    path('request_password_recovery/', views.RequestPasswordResetView.as_view(), name='Request_Recovery'),
    path('verify_code/', views.ValidateRecoveryCodeView.as_view(), name='Validate_Code'),
    path('reset_password/', views.PasswordResetConfirmView.as_view(), name='Reset_password'),


    # Get bucket list INFO...
    path('routinesGlobal', views.getRoutinesGlobal, name='Routine_Global'),
]
