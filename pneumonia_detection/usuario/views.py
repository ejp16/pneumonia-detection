from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView
from django.views import View
from django.shortcuts import render, get_object_or_404
from .models import *
from django.contrib import messages
from django.shortcuts import redirect
from .forms import RegisterForm, LoginForm, AntecedentesForm, PacienteForm, InformeForm
from .utils import Modelo
from django.urls import reverse
import string
import random

class RegistroView(CreateView):
    template_name = 'registro.html'
    form_class = RegisterForm
    success_url = '/usuario/login'
    model = MedicoUsuario()
    def form_valid(self, form_class):
        form_class.save()
        return super().form_valid(form_class)
    
class LoginView(View):
    template_name = "login.html"
    form_class = LoginForm()
    def get(self, request):
        if 'email_medico' not in request.session:
            return render(request, self.template_name, {'form': self.form_class})
        else:
            return redirect('index_medico')

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            medico_user = MedicoUsuario.objects.filter(email=email).first()
            paciente_user = PacienteUsuario.objects.filter(email=email).first()
            print(medico_user and medico_user.password == password)
            if medico_user and medico_user.password == password:
                request.session['email_medico'] = email
                return redirect('index_medico')
            elif paciente_user and paciente_user.password == password:
                request.session['email_paciente'] = email
                return redirect('index_paciente')
            else:
                messages.warning(request, 'Correo o contraseña incorrectos')
            return redirect('login')

class IndexMedicoView(View):
    template_name = 'index_medico.html'
    def get(self, request):
        if 'email_medico' in request.session:
            email = request.session.get('email_medico')
            user_medico = MedicoUsuario.objects.filter(email=email).first()
            pacientes = Paciente.objects.filter(id_medico = user_medico.id).all()
            return render(request, self.template_name, {'pacientes': pacientes, })
        else:
            return redirect('login')

class Indexpaciente(View):
    def get(self, request):
        if 'email_paciente' in request.session:
            email = request.session.get('email')
            paciente = Paciente.objects.filter(email = email).first()
            reports = Informe.objects.filter(id = pacientes.id)
            return render(request, self.template_name, {'paciente': paciente, 'reports': reports})
        else:
            return redirect('login')

class CrearPaciente(CreateView):
    template_name = 'registrar_paciente.html'
    form_class = PacienteForm
    success_url = 'usuario/index_medico'
    model = Paciente

    def form_valid(self, form_class):
        form = form_class.save(commit=False)
        email = self.request.session.get('email_medico')
        user_medico = MedicoUsuario.objects.filter(email=email).first()
        print(user_medico)
        form.id_medico_id = user_medico.id
        form.save()
        return redirect('index_medico')
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        print(form.errors)
        return redirect('index_medico')
    
class EditarPaciente(UpdateView):
    template_name = 'registrar_paciente.html'
    form_class = PacienteForm
    model = Paciente
    def get_success_url(self):
        print(self.object.id)
        return reverse('ver_paciente', args=[self.object.id])

class VerPaciente(View):
    template_name = 'ver_paciente.html'
    def get(self, request, **kwargs):
        email = self.request.session.get('email_medico')
        user_medico = MedicoUsuario.objects.filter(email = email).first()
        id_paciente = kwargs['pk']
        paciente = Paciente.objects.get(id = id_paciente)
        if paciente.id == user_medico.id:
            antecedentes = AntecedentesPaciente.objects.filter(id_paciente = paciente.id).all()
            imagenes = Imagen.objects.filter(id_paciente = paciente.id).all()
            analisis = Analisis.objects.filter(id_imagen__in = imagenes).all()
            informes = Informe.objects.filter(id_paciente = paciente.id).all()
            antecedentesID = AntecedentesID.objects.all()
            lista_antecedentes = zip(antecedentesID, antecedentes)
            
            return render(request, self.template_name, {'paciente': paciente, 'antecedentes': lista_antecedentes, 'imagenes': imagenes, 'analisis': analisis, 'informes': informes})
        else:
            return redirect('index_medico')

class RegistrarAntecedentes(FormView):
    template_name = 'registrar_antecedentes.html'
    form_class = AntecedentesForm
    
    def get(self, request, **kwargs):
        if 'email_medico' in request.session:
            id_paciente = kwargs['pk']
            paciente = Paciente.objects.get(id=id_paciente)
            return render(request, self.template_name, {'form': self.form_class, 'paciente': paciente})
    
    def post(self, request, **kwargs):
        form = AntecedentesForm(request.POST)
        id_paciente = request.POST.get('pk')
        paciente = Paciente.objects.get(id=id_paciente)
        if form.is_valid():
            antecedentesID = AntecedentesID.objects.all()
            data = [
                form.cleaned_data['medicos'],
                form.cleaned_data['quirurgicos'],
                form.cleaned_data['alergologicos'],
                form.cleaned_data['cardiovasculares'],
                form.cleaned_data['sociales'],
                form.cleaned_data['familiares'],
                form.cleaned_data['vacunacion']
            ]
            for indice, antecedente in enumerate(antecedentesID):
                AntecedentesPaciente(
                    id_antecedentesID=antecedente, 
                    antecedente_descrip=data[indice], 
                    id_paciente=paciente).save()
                
            return redirect('index_medico')
        else:

            return redirect('registrar_antecedentes', pk=id_paciente)
   

class RegistrarAnalisis(FormView):
    template_name = 'registrar_analisis.html'
    def get(self, request, **kwargs):
        if 'email_medico' in request.session:
            email = request.session['email_medico']
            user_medico = MedicoUsuario.objects.filter(email = email).first()
            id_paciente = kwargs['pk']
            paciente = Paciente.objects.get(id=id_paciente)
            return render(request, self.template_name, {'paciente': paciente})
        else:
            return redirect('index_medico')
    
    def post(self, request, **kwargs):
        imagen = request.FILES['radiografia']
        email = request.session.get('email')
        id_paciente = request.POST.get('pk')
        user_medico = MedicoUsuario.objects.filter(email=email).first()
        paciente = Paciente.objects.get(id=id_paciente)
        Imagen(imagen = imagen, id_paciente=paciente).save()
        img = Imagen.objects.all().last()
        img_url = img.imagen.url
        modelo = Modelo(img_url)
        respuesta = modelo.prediccion()
        Analisis(
            resultado=respuesta['resultado'],
            probabilidad=respuesta['probabilidad'],
            recomendaciones='lol',
            id_imagen=img
        ).save()
        return redirect('ver_paciente', pk=id_paciente)

class RegistrarInforme(FormView):
    template_name = 'registrar_informe.html'
    form_class = InformeForm
    model = Informe
    def get(self, request, **kwargs):
        if 'email_medico' in request.session:
            email = request.session.get('email_medico')
            user_medico = MedicoUsuario.objects.filter(email=email).first()
            id_paciente = kwargs.get('pk')
            paciente = Paciente.objects.get(id=id_paciente)
            img = Imagen.objects.filter(id_paciente_id = id_paciente).all()
            analisis = Analisis.objects.filter(id_imagen__in = img).all()
            return render(request, self.template_name, {'form': self.form_class, 'paciente': paciente, 'analisis': analisis})
        else:
            return redirect('ver_paciente', pk=id_paciente)

    def form_valid(self, form_class):
        form = form_class.save(commit=False)            
        email = self.request.session.get('email_medico')
        id_paciente = self.request.POST.get('pk')
        user_medico = MedicoUsuario.objects.filter(email=email).first()
        analisis_id = self.request.POST.get('analisis_id')
        form.id_medico_id = user_medico.id
        form.id_paciente_id = id_paciente
        form.id_analisis_id = analisis_id
        form.save()
        return redirect('ver_paciente', pk=id_paciente)

class EditarAntecedentes(FormView):
    template_name = 'registrar_antecedentes.html'
    form_class = AntecedentesForm
    
    def get(self, request, **kwargs):
        if 'email_medico' in request.session:
            id_paciente = kwargs['pk']
            paciente = Paciente.objects.get(id=id_paciente)
            id = kwargs['pk']
            context = {}
            data = list(AntecedentesPaciente.objects.filter(id_paciente = id).order_by('-id_antecedentesID'))
            antecedentesIds = list(AntecedentesID.objects.all())
            initial_data = {}
            for index in range(len(data)):
                initial_data[antecedentesIds[index].tipo_antecedente.lower()] = data[index].antecedente_descrip
            
            form = AntecedentesForm(initial=initial_data)
            return render(request, self.template_name, {'form': form, 'paciente': paciente})

        else:
            return redirect('/index_medico')

    def post(self, request, **kwargs):
        form = self.form_class(request.POST)
        id_paciente = request.POST.get('pk')
        if form.is_valid():

            paciente = Paciente.objects.get(id=id_paciente)
            antecedentesID = AntecedentesID.objects.all()
            antecedentes_paciente = AntecedentesPaciente.objects.filter(id_paciente=paciente.id).all()
            data = [
                form.cleaned_data['medicos'],
                form.cleaned_data['quirurgicos'],
                form.cleaned_data['alergologicos'],
                form.cleaned_data['cardiovasculares'],
                form.cleaned_data['sociales'],
                form.cleaned_data['familiares'],
                form.cleaned_data['vacunacion']
            ]
            print(antecedentes_paciente)
            for indice, tipo in enumerate(antecedentes_paciente):
                tipo.antecedente_descrip = antecedente_descrip=data[indice]
                tipo.save()
            return redirect('index_medico')
        
        else:
            return redirect('index_paciente', pk=id_paciente)
    

class Logout(View):
    def get(self, request):
        request.session.pop('email_medico')
        return redirect('login')
