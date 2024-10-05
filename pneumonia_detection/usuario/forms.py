from django import forms
from usuario.models import Paciente, Informe, AntecedentesPaciente, User
from django.contrib.auth.forms import UserCreationForm  

class FormRegistro(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1'
        ]

    
    username = forms.CharField(label='Nombre', min_length=12, max_length=28, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, label='Correo electronico', max_length=24, min_length=15, widget=forms.EmailInput(
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
            'edad',
            'fecha_nacimiento',
            ]
    
    CHOICES = (
        ('H', 'Hombre'),
        ('M', 'Mujer')
    )

    nombre = forms.CharField(label='Nombre', required=True, widget=forms.TextInput(attrs={'class': 'form-control',}))
    apellido = forms.CharField(label='Apellido', required=True, widget=forms.TextInput(attrs={'class': 'form-control',}))
    cedula = forms.CharField(label='Cedula', required=True, widget=forms.TextInput(attrs={'class': 'form-control',}))
    sexo = forms.ChoiceField(choices=CHOICES)
    peso = forms.CharField(label='Peso en Kg', required=True, widget=forms.TextInput(attrs={'class': 'form-control',}))
    altura = forms.CharField(label='Altura en cm', required=True, widget=forms.TextInput(attrs={'class': 'form-control',}))
    telefono = forms.CharField(label='Telefono', required=True, widget=forms.TextInput(attrs={'class': 'form-control', }))
    email = forms.EmailField(required=True, label='Correo electronico', widget=forms.EmailInput(
        attrs={'class': 'form-control'}
    ))
    direccion = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control'}))
    edad = forms.CharField(label='Edad', max_length=3, required=True, widget=forms.TextInput(attrs={'class': 'form-control',}))
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))

class AntecedentesForm(forms.Form):
    
    medicos = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control'}))
    quirurgicos = forms.CharField(widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control'}))
    alergologicos = forms.CharField(widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control'}))
    cardiovasculares = forms.CharField(widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control'}))
    sociales = forms.CharField(widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control'}))
    familiares = forms.CharField(widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control'}))
    vacunacion = forms.CharField(widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control'}))

class InformeForm(forms.ModelForm):
    class Meta:
        model = Informe
        fields = [
            'motivo_consulta',
            'observaciones',
            'recomendaciones',
            'medicacion',
        ]

    motivo_consulta = forms.CharField(label='Motivo de la consulta', required=True, widget=forms.TextInput(attrs={'class': 'form-control',}))
    observaciones = forms.CharField(widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control'}))
    recomendaciones = forms.CharField(widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control'}))
    medicacion = forms.CharField(widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control'}))


