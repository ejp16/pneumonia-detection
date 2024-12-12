from django import forms
from usuario.models import Paciente, Informe, AntecedentesPaciente, User
from django.contrib.auth.forms import UserCreationForm, BaseUserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import datetime
class FormRegistro(BaseUserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1'
        ]

    
    username = forms.CharField(label='Nombre', min_length=12, max_length=28, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, label='Correo electronico', max_length=40, min_length=11, widget=forms.EmailInput(
        attrs={'class': 'form-control'}
    ))

    password1 = forms.CharField(label='Contraseña', required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirmar contraseña', required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo electronico', widget=forms.EmailInput(
        attrs={'class': 'form-control'}
    ))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'registro'}))

    class Meta:
        fields = ['email', 'password']
    
class FormRegistrarPaciente(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            'nombre', 
            'apellido', 
            'cedula', 
            'sexo',
            'peso',
            'altura',
            'telefono', 
            'email',
            'direccion',
            'fecha_nacimiento',
            ]
    
    CHOICES = (
        ('H', 'Hombre'),
        ('M', 'Mujer')
    )

    nombre = forms.CharField(label='Nombre', required=True, max_length=40, validators=[RegexValidator('[0-9+-/%]', inverse_match=True)], widget=forms.TextInput(attrs={'class': 'form-control',}))
    apellido = forms.CharField(label='Apellido', required=True, max_length=40, validators=[RegexValidator('[0-9+-/%]', inverse_match=True)], widget=forms.TextInput(attrs={'class': 'form-control',}))
    cedula = forms.CharField(label='Cédula', required=True, max_length=12, validators=[RegexValidator('[a-z+-/%]', inverse_match=True)], widget=forms.TextInput(attrs={'class': 'form-control',}))
    sexo = forms.ChoiceField(choices=CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    peso = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control',}))
    altura = forms.FloatField(label='Altura', required=True, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '01'}) )
    telefono = forms.CharField(label='Teléfono', required=True, max_length=16, validators=[RegexValidator('[a-z+-/%-]', inverse_match=True, message='Usar solo números en este campo')], widget=forms.TextInput(attrs={'class': 'form-control', }))
    email = forms.EmailField(required=True, label='Correo electronico', widget=forms.EmailInput(
        attrs={'class': 'form-control'}
    ))
    direccion = forms.CharField(required=True, max_length=255, widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control'}))
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'max': datetime.datetime.now().date(),}, format="d%m%Y%"))

class AntecedentesForm(forms.Form):
    
    medicos = forms.CharField(empty_value='No refiere', required=False, widget=forms.Textarea(attrs={"rows":"4", 'class': 'form-control antecedentes-form-control'}))
    quirurgicos = forms.CharField(empty_value='No refiere', required=False, widget=forms.Textarea(attrs={"rows":"4", 'class': 'form-control antecedentes-form-control'}))
    alergologicos = forms.CharField(empty_value='No refiere', required=False, widget=forms.Textarea(attrs={"rows":"4", 'class': 'form-control antecedentes-form-control'}))
    cardiovasculares = forms.CharField(empty_value='No refiere', required=False, widget=forms.Textarea(attrs={"rows":"4", 'class': 'form-control antecedentes-form-control'}))
    sociales = forms.CharField(empty_value='No refiere', required=False, widget=forms.Textarea(attrs={"rows":"4", 'class': 'form-control antecedentes-form-control'}))
    familiares = forms.CharField(empty_value='No refiere', required=False, widget=forms.Textarea(attrs={"rows":"4", 'class': 'form-control antecedentes-form-control'}))
    vacunacion = forms.CharField(empty_value='No refiere', required=False, widget=forms.Textarea(attrs={"rows":"4", 'class': 'form-control antecedentes-form-control '}))

class InformeForm(forms.ModelForm):
    class Meta:
        model = Informe
        fields = [
            'inicio_enfermedad',
            'caracterizado',
            'examenes',
            'antecedentes_importancia',
            'frecuencia_cardiaca',
            'frecuencia_respiratoria',
            'tension_arterial',
            'saturacion_oxigeno',
            'recomendacion',


        ]

    inicio_enfermedad = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'max': datetime.datetime.now().date(),}, format="d%m%Y%"))
    caracterizado = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows":"3", 'class': 'patient-report-input form-control'}))
    examenes = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows":"3", 'class': 'patient-report-input form-control'}))
    antecedentes_importancia = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows":"3", 'class': 'patient-report-input form-control'}))
    frecuencia_cardiaca = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control',}))
    frecuencia_respiratoria = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control',}))
    tension_arterial = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control',}))
    saturacion_oxigeno = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control',}))
    recomendacion = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'patient-report-input form-control', 'rows': 3}))

class ImagenForm(forms.Form):
    image_field = forms.ImageField(required=True,)