from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .backend import EmailBackend
from .models import *
from django.contrib import messages
from .forms import FormRegistro, LoginForm, AntecedentesForm, FormRegistrarPaciente, InformeForm
from .utils import Modelo
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string


class RegistroView(CreateView):
    template_name = 'registro.html'
    form_class = FormRegistro
    success_url = '/usuario/login'
    model = User
    def form_valid(self, form_class):
        form_class.save()
        return redirect('login')
    
    def form_invalid(self, form_class):
        response = form_class.errors
        print(response)
        return redirect('register')
    
    
class LoginView(View):
    template_name = "login.html"
    form_class = LoginForm()
    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = EmailBackend.authenticate(self, request=request, email=email, password=password)
            if user and user.rol == 'Medico':
                login(request, user, backend='usuario.backend.EmailBackend')
                return redirect('index_medico')
            elif user and user.rol == 'Paciente':
                login(request, user, backend='usuario.backend.EmailBackend')
                return redirect('index_paciente')
            else:
                print('malas credenciales')
                messages.warning(request, 'Correo o contraseña incorrectos')
            return redirect('login')


class IndexMedicoView(LoginRequiredMixin, View):
    template_name = 'index_medico.html'
    permission_denied_message = "You are not allowed here."
    raise_exception = True  # Raise exception when no access instead of redirect
    def get(self, request):
        if request.user.rol == 'Medico':
            user = request.user
            pacientes = Paciente.objects.filter(id_medico = user.id).all()
            context = {
                'pacientes': pacientes
            }
            return render(request, self.template_name, context)
        return redirect('index_paciente')

class IndexPaciente(LoginRequiredMixin, View):
    template_name = 'index_paciente.html'
    def get(self, request):
        if request.user.rol == 'Paciente':
            user_paciente = request.user
            print(user_paciente)
            paciente = Paciente.objects.get(id_usuario_paciente_id = user_paciente.id)
            reports = Informe.objects.filter(id = user_paciente.id).all()
            return render(request, self.template_name, {'paciente': paciente, 'reports': reports})
        return redirect('index_medico')

class RegistrarPacienteView(LoginRequiredMixin, CreateView):
    template_name = 'registrar_paciente.html'
    form_class = FormRegistrarPaciente
    success_url = 'usuario/index_medico'
    model = Paciente

    def get(self, request):
        if request.user.rol == 'Medico':
            return render(request, self.template_name, {'form': self.form_class})
        return redirect('index_paciente')

    def form_valid(self, form_class):
        form = form_class.save(commit=False)
        user = self.request.user
        form.id_medico_id = user.id
        clave = get_random_string(8)
        print(f'CLAVE DEL PACIENTE: {clave}')
        try:
            user_paciente = User.objects.create_user(
                username=form.nombre,
                email=form.email,
                password=clave,
                rol='Paciente'
            )
            form.id_usuario_paciente_id = user_paciente.id
            form.save()
        except:
            print('ESTE CORREO PERTENECE A OTRO PACIENTE')
            return redirect('registrar_paciente')
    
        return redirect('index_medico')
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        print(form.errors)
        return redirect('index_medico')

class VerPaciente(LoginRequiredMixin, View):
    template_name = 'ver_paciente.html'
    def get(self, request, **kwargs):
        if request.user.rol == 'Medico':
            
            id_paciente = kwargs['pk']
            paciente = Paciente.objects.get(id = id_paciente)
            user_medico = self.request.user
            if paciente.id_medico_id == user_medico.id:
                antecedentes = AntecedentesPaciente.objects.filter(id_paciente = paciente.id).all()
                imagenes = Imagen.objects.filter(id_paciente = paciente.id).all()
                analisis = Analisis.objects.filter(id_imagen__in = imagenes).all()
                informes = Informe.objects.filter(id_paciente = paciente.id).all()
                antecedentesID = AntecedentesID.objects.all()
                lista_antecedentes = list(zip(antecedentesID, antecedentes))
                return render(request, self.template_name, {'paciente': paciente, 'antecedentes': lista_antecedentes, 'imagenes': imagenes, 'analisis': analisis, 'informes': informes})
            else:
                return redirect('index_medico')
        return redirect('index_paciente')
class EditarPaciente(LoginRequiredMixin, UpdateView):
    template_name = 'registrar_paciente.html'
    form_class = FormRegistrarPaciente
    model = Paciente

    def get(self, request):
        if request.user.rol == 'Medico':
            return render(request, self.template_name, {'form': self.form_class})
        return redirect('index_paciente')

    def get_success_url(self):
        return reverse('ver_paciente', args=[self.object.id])

class RegistrarAntecedentes(LoginRequiredMixin, FormView):
    template_name = 'registrar_antecedentes.html'
    form_class = AntecedentesForm
    
    def get(self, request, **kwargs):
        if request.user.rol == 'Medico':
            id_paciente = kwargs['pk']
            paciente = Paciente.objects.get(id=id_paciente)
            return render(request, self.template_name, {'form': self.form_class, 'paciente': paciente})
        return redirect('index_paciente')

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
                AntecedentesPaciente.objects.create(
                    id_antecedentesID=antecedente, 
                    antecedente_descrip=data[indice], 
                    id_paciente=paciente)
                
            return redirect('index_medico')
        else:
            print('ERRORES DEL FORM: ')
            print(form.errors)
            return redirect('registrar_antecedentes', pk=id_paciente)
   

class RegistrarAnalisis(LoginRequiredMixin, FormView):
    template_name = 'registrar_analisis.html'
    def get(self, request, **kwargs):
        if request.user.rol == 'Medico':
            id_paciente = kwargs['pk']
            paciente = Paciente.objects.get(id=id_paciente)
            return render(request, self.template_name, {'paciente': paciente})
        return redirect('index_paciente')    

    def post(self, request, **kwargs):
        imagen = request.FILES['radiografia']
        id_paciente = request.POST.get('pk')
        paciente = Paciente.objects.get(id=id_paciente)
        antecedentes = list(AntecedentesPaciente.objects.filter(id_paciente = paciente.id).order_by('-id_antecedentesID'))
        img = Imagen.objects.create(imagen = imagen, id_paciente=paciente)
        img_url = img.imagen.url
        modelo = Modelo(img_url)
        prediccion = modelo.prediccion()
        recomendacion = modelo.prompt(
            edad=paciente.edad,
            peso=paciente.peso,
            altura=paciente.altura,
            antecedentes=antecedentes
        )
        Analisis.objects.create(
            resultado=prediccion['resultado'],
            probabilidad=prediccion['probabilidad'],
            recomendaciones=recomendacion,
            id_imagen=img
        )
        return redirect('ver_paciente', pk=id_paciente)

class RegistrarInforme(LoginRequiredMixin, FormView):
    template_name = 'registrar_informe.html'
    form_class = InformeForm
    model = Informe
    def get(self, request, **kwargs):
        if request.user.rol == 'Medico':
            id_paciente = kwargs.get('pk')
            paciente = Paciente.objects.get(id=id_paciente)
            img = Imagen.objects.filter(id_paciente_id = id_paciente).all()
            analisis = Analisis.objects.filter(id_imagen__in = img).all()
            return render(request, self.template_name, {'form': self.form_class, 'paciente': paciente, 'analisis': analisis})
        return redirect('index_paciente')

    def form_valid(self, form_class):
        form = form_class.save(commit=False)            
        id_paciente = self.request.POST.get('pk')
        analisis_id = self.request.POST.get('analisis_id')
        user_medico = self.request.user
        form.id_medico_id = user_medico.id
        form.id_paciente_id = id_paciente
        form.id_analisis_id = analisis_id
        form.save()
        return redirect('ver_paciente', pk=id_paciente)

class EditarAntecedentes(LoginRequiredMixin, FormView):
    template_name = 'registrar_antecedentes.html'
    form_class = AntecedentesForm
    
    def get(self, request, **kwargs):
        if request.user.rol == 'Medico':
            id_paciente = kwargs['pk']
            paciente = Paciente.objects.get(id=id_paciente)
            id = kwargs['pk']
            data = list(AntecedentesPaciente.objects.filter(id_paciente = id).order_by('-id_antecedentesID'))
            antecedentesIds = list(AntecedentesID.objects.all())
            initial_data = {}
            for index in range(len(data)):
                initial_data[antecedentesIds[index].tipo_antecedente.lower()] = data[index].antecedente_descrip
            
            form = AntecedentesForm(initial=initial_data)
            return render(request, self.template_name, {'form': form, 'paciente': paciente})
        return redirect('index_paciente')

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
            for indice, tipo in enumerate(antecedentes_paciente):
                tipo.antecedente_descrip = antecedente_descrip=data[indice]
                tipo.save()
            return redirect('ver_paciente', pk=id_paciente)
        
        else:
            return redirect('index_paciente', pk=id_paciente)


class LogoutMedico(View):
    def get(self, request):
        logout(request)
        return redirect('login')

class LogoutPaciente(View):
    def get(self, request):
        logout(request)
        return redirect('login')
    
