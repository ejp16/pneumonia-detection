from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [ 
    path('register/', views.RegistroView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('index_medico/', views.IndexMedicoView.as_view(), name='index_medico'),

    path('index_paciente/', views.IndexPaciente.as_view(), name='index_paciente'),
    path('registrar_paciente/', views.RegistrarPacienteView.as_view(), name='registrar_paciente'),
    path('ver_paciente/<int:pk>', views.VerPaciente.as_view(), name='ver_paciente'),
    path('editar_paciente/<int:pk>', views.EditarPaciente.as_view(), name='editar_paciente'),

    path('registrar_antecedentes/<int:pk>', views.RegistrarAntecedentes.as_view(), name='registrar_antecedentes'),
    path('editar_antecedentes/<int:pk>', views.EditarAntecedentes.as_view(), name='editar_antecedentes'),
    path('registrar_analisis/<int:pk>', views.RegistrarAnalisis.as_view(), name='registrar_analisis'),
    path('registrar_informe/<int:pk>', views.RegistrarInforme.as_view(), name='registrar_informe'),

    path('reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetView.as_view(), name='password_reset_complete'),

    path('buscar/', views.BusquedaView.as_view(), name='buscar'),

    path('logout/', views.Logout.as_view(), name='logout'),
    
]
