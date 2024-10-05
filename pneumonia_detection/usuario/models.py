from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.models import Group

class CustomUserManager(UserManager):
    pass

class User(AbstractUser):
    MEDICO = 1
    PACIENTE = 1
    ROLE_CHOICES = (
        (MEDICO, 'Medico'),
        (PACIENTE, 'Paciente')
    )

    username = models.CharField(max_length=50, unique=False)
    email = models.EmailField(max_length=100, unique=True)
    rol = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Medico')
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)


class Paciente(models.Model):
    nombre = models.CharField(max_length=40, )
    apellido = models.CharField(max_length=40, )
    cedula = models.CharField(max_length=12, )
    sexo = models.CharField(max_length=6, )
    peso = models.CharField(max_length=3, )
    altura = models.IntegerField()
    telefono = models.CharField(max_length=16, )
    email = models.EmailField()
    direccion = models.CharField(max_length=255, )
    edad = models.CharField(max_length=3, )
    fecha_nacimiento = models.DateField()
    registro = models.DateField(auto_now=True)
    id_medico = models.ForeignKey(User, on_delete=models.PROTECT, related_name='id_medico')
    id_usuario_paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='id_paciente')

class AntecedentesID(models.Model):
    tipo_antecedente = models.CharField(max_length=20)

class AntecedentesPaciente(models.Model):
    id_antecedentesID = models.ForeignKey(AntecedentesID, on_delete=models.PROTECT)
    antecedente_descrip = models.TextField()
    id_paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)

class Imagen(models.Model):
    imagen = models.ImageField(upload_to='radiografias/')
    id_paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)

class Analisis(models.Model):
    resultado = models.CharField(max_length=8, )
    probabilidad = models.CharField(max_length=4, )
    recomendaciones = models.CharField(max_length=255, )
    id_imagen = models.ForeignKey(Imagen, on_delete=models.PROTECT)

class Informe(models.Model):
    motivo_consulta = models.CharField(max_length=255, )
    observaciones = models.TextField()
    recomendaciones = models.TextField()
    medicacion = models.CharField(max_length=255, )
    id_medico = models.ForeignKey(User, on_delete=models.PROTECT)
    id_paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)
    id_analisis = models.ForeignKey(Analisis, on_delete=models.PROTECT)



