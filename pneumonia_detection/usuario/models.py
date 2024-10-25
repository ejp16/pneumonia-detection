from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=False)  # Permitir duplicados
    email = models.EmailField(unique=True)  # Asegurarte de que los correos sean únicos
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
    
class Paciente(models.Model):
    nombre = models.CharField(max_length=40, )
    apellido = models.CharField(max_length=40, )
    cedula = models.CharField(max_length=12, )
    sexo = models.CharField(max_length=1, )
    peso = models.CharField(max_length=3, )
    altura = models.IntegerField()
    telefono = models.CharField(max_length=16, )
    email = models.EmailField()
    direccion = models.CharField(max_length=255, )
    edad = models.IntegerField()
    fecha_nacimiento = models.DateField()
    registro = models.DateField(auto_now=True)
    id_usuario_paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='id_paciente')

class RelacionMedicoPaciente(models.Model):
    id_medico = models.ForeignKey(User, on_delete=models.PROTECT, related_name='id_medico')
    id_paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)

class AntecedentesID(models.Model):
    tipo_antecedente = models.CharField(max_length=20)

class AntecedentesPaciente(models.Model):
    id_antecedentesID = models.ForeignKey(AntecedentesID, on_delete=models.PROTECT)
    antecedente_descrip = models.TextField(blank=True, null=True)
    id_paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)

class Imagen(models.Model):
    imagen = models.ImageField(upload_to='radiografias/')
    id_paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)

class Analisis(models.Model):
    resultado = models.CharField(max_length=8, )
    probabilidad = models.CharField(max_length=4, )
    recomendaciones = models.TextField(blank=True, null=True)
    id_imagen = models.ForeignKey(Imagen, on_delete=models.PROTECT)
    id_medico = models.ForeignKey(User, on_delete=models.PROTECT)
    id_paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, null=True)
    fecha_analisis = models.DateField(auto_now=True)

class Informe(models.Model):
    motivo_consulta = models.CharField(max_length=255, )
    fecha_consulta = models.DateField()
    observaciones = models.TextField()
    recomendaciones = models.TextField()
    medicacion = models.CharField(max_length=255, )
    fecha_informe = models.DateField(auto_now=True)
    id_medico = models.ForeignKey(User, on_delete=models.PROTECT)
    id_paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)



