from django import forms
from usuario.models import Usuario, Analisis, HistoriaPaciente

class RegistroForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'password']
    nombre = forms.CharField(label='Nombre', min_length=12, max_length=28, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, label='Correo electronico', max_length=24, min_length=15, widget=forms.EmailInput(
        attrs={'class': 'form-control'}
    ))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class LoginForm(forms.Form):
    class Meta:
        fields = ['email', 'password']
    email = forms.EmailField(label='Correo electronico', widget=forms.EmailInput(
        attrs={'class': 'form-control'}
    ))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'registro'}))

class HistoriaPacientes(forms.ModelForm):
    class Meta:
        model = HistoriaPaciente
        fields = ['nombre_paciente', 'edad', 'cedula', 'telefono', 'email_paciente', 'observaciones']

    nombre_paciente = forms.CharField(label='Nombre', required=True, widget=forms.TextInput(attrs={'class': 'form-control',}))
    edad = forms.CharField(label='Edad', max_length=3, required=True, widget=forms.TextInput(attrs={'class': 'form-control',}))
    cedula = forms.CharField(label='Cedula', required=True, widget=forms.TextInput(attrs={'class': 'form-control',}))
    telefono = forms.CharField(label='Telefono', required=True, widget=forms.TextInput(attrs={'class': 'form-control', }))
    email_paciente = forms.EmailField(required=True, label='Correo electronico', widget=forms.EmailInput(
        attrs={'class': 'form-control'}
    ))
    observaciones = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control'}))

