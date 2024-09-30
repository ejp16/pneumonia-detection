from django.urls import path
from . import views

urlpatterns = [ 
    path('register/', views.RegistroView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('index_medico/', views.IndexMedico.as_view(), name='index_medico'),
    path('index_paciente/', views.IndexPaciente.as_view(), name='index_paciente'),
    path('crear_paciente/', views.CrearPaciente.as_view(), name='crear_paciente'),
    path('ver_paciente/<int:pk>', views.VerPaciente.as_view(), name='ver_paciente'),
    path('registrar_antecedentes/<int:pk>', views.RegistrarAntecedentes.as_view(), name='registrar_antecedentes'),
    path('editar_paciente/<int:pk>', views.EditarPaciente.as_view(), name='editar_paciente'),
    path('registrar_analisis/<int:pk>', views.RegistrarAnalisis.as_view(), name='registrar_analisis'),
    path('registrar_informe/<int:pk>', views.RegistrarInforme.as_view(), name='registrar_informe'),
    path('editar_antecedentes/<int:pk>', views.EditarAntecedentes.as_view(), name='editar_antecedentes'),
    path('logout_medico/', views.LogoutMedico.as_view(), name='logout_medico'),
    path('logout_paciente/', views.LogoutPaciente.as_view(), name='logout_paciente')
    
]
