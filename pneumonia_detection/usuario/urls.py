from django.urls import path
from . import views

urlpatterns = [ 
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('registrar_paciente/', views.RegistrarHistoria.as_view(), name='registrar_paciente'),
    path('registrar_analisis/', views.RegistrarAnalisisView.as_view(), name='registrar_analisis'),
    path('historia/<int:id>', views.VerHistoria.as_view(), name='ver_historia'),
    path('historia/editar/<pk>', views.EditarHistoria.as_view(), name='editar_historia'),
    path('historia/borrar/<pk>', views.BorrarHistoria.as_view(), name='borrar_historia'),
    path('logout/', views.Logout.as_view(), name='logout')
    
]
