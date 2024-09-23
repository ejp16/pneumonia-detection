from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=28)
    email = models.CharField(max_length=24, unique=True)
    password = models.CharField(max_length=16)

class HistoriaPaciente(models.Model):
    nombre_paciente = models.CharField(max_length=28, null=True)
    edad = models.CharField(max_length=3)
    cedula = models.CharField(max_length=8)
    telefono = models.CharField(max_length=11)
    email_paciente = models.CharField(max_length=24)
    observaciones = models.TextField()
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, default=1)

class Imagenes(models.Model):
    imagen = models.ImageField(upload_to='radiografias/')
    id_Hpaciente = models.ForeignKey(HistoriaPaciente, on_delete=models.CASCADE, default=1)

class Analisis(models.Model):
    resultado = models.CharField(max_length=8)
    probabilidad = models.CharField(max_length=4, null=True)
    recomendaciones = models.TextField(max_length=500)
    id_imagen = models.ForeignKey(Imagenes, on_delete=models.CASCADE, default=1)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, default=1)


""" 
class AnalisisPaciente(models.Model):
    resultado = models.CharField(max_length=8)
    probabilidad = models.CharField(max_length=4)
    recomendaciones = models.TextField(max_length=500)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_imagen = models.ForeignKey(Imagenes, on_delete=models.CASCADE, null=True)
 """


