from django.db import models

class MedicoUsuario(models.Model):
    nombre = models.CharField(max_length=255, )
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, )

class Paciente(models.Model):
    nombre = models.CharField(max_length=255, )
    apellido = models.CharField(max_length=255, )
    cedula = models.CharField(max_length=255, )
    sexo = models.CharField(max_length=255, )
    peso = models.CharField(max_length=255, )
    altura = models.IntegerField()
    telefono = models.CharField(max_length=255, )
    correo = models.EmailField()
    direccion = models.CharField(max_length=255, )
    edad = models.CharField(max_length=255, )
    fecha_nacimiento = models.DateField()
    registro = models.DateField(auto_now=True)
    id_medico = models.ForeignKey(MedicoUsuario, on_delete=models.PROTECT)

class PacienteUsuario(models.Model):
    id_paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)
    clave_acceso = models.CharField(max_length=255, )
    email = models.CharField(max_length=255, )
   
class AntecedentesID(models.Model):
    tipo_antecedente = models.CharField(max_length=50, null=True)

class AntecedentesPaciente(models.Model):
    id_antecedentesID = models.ManyToManyField(AntecedentesID)
    antecedente_descrip = models.TextField()
    id_paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)

class Imagen(models.Model):
    imagen = models.ImageField(upload_to='radiografias/')
    id_paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)

class Analisis(models.Model):
    resultado = models.CharField(max_length=255, )
    probabilidad = models.CharField(max_length=255, )
    recomendaciones = models.CharField(max_length=255, )
    id_imagen = models.ForeignKey(Imagen, on_delete=models.PROTECT)

class Informe(models.Model):
    motivo_consulta = models.CharField(max_length=255, )
    observaciones = models.TextField()
    recomendaciones = models.TextField()
    medicacion = models.CharField(max_length=255, )
    id_medico = models.ForeignKey(MedicoUsuario, on_delete=models.PROTECT)
    id_paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)
    id_analisis = models.ForeignKey(Analisis, on_delete=models.PROTECT)



