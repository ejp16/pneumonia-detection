from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView, ListView
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .backend import EmailBackend
from .models import *
from django.contrib import messages
from .forms import FormRegistro, LoginForm, AntecedentesForm, FormRegistrarPaciente, InformeForm
from .utils import Modelo, EnviarMail
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import UserPassesTestMixin

from django.template.loader import render_to_string

class MedicoUserMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Medico').exists()

class PacienteUserMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Paciente').exists()

class RegistroView(CreateView):
    template_name = 'registro.html'
    form_class = FormRegistro
    success_url = '/usuario/login'
    model = User
    def form_valid(self, form_class):
        user = form_class.save(commit=False)
        group = Group.objects.get(name='Medico')
        user.save()
        user.groups.add(group)
        
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
            if user and user.groups.filter(name='Medico').exists():
                login(request, user, backend='usuario.backend.EmailBackend')
                return redirect('index_medico')
            elif user and user.groups.filter(name='Paciente').exists():
                login(request, user, backend='usuario.backend.EmailBackend')
                return redirect('index_paciente')
            else:
                print('malas credenciales')
                messages.warning(request, 'Correo o contraseña incorrectos')
            return redirect('login')

class IndexMedicoView(MedicoUserMixin, ListView):
    template_name = 'index_medico.html'
    model = Paciente
    context_object_name = 'pacientes'

    def get_queryset(self):
        return Paciente.objects.select_related('id_medico').filter(id_medico = self.request.user.id)
    
class IndexPaciente(PacienteUserMixin, View):
    template_name = 'index_paciente.html'
    def get(self, request):
        user_paciente = request.user
        print(user_paciente.id)
        paciente = Paciente.objects.get(id_usuario_paciente_id = user_paciente.id)
        imagenes = Imagen.objects.filter(id_paciente=paciente.id).all()
        analisis = Analisis.objects.filter(id_imagen__in=imagenes).all()
        informes = Informe.objects.filter(id_paciente_id = paciente.id).all()
        print(informes)
        return render(request, self.template_name, {'paciente': paciente, 'informes': informes, 'analisis': analisis})

class RegistrarPacienteView(MedicoUserMixin, CreateView):
    template_name = 'registrar_paciente.html'
    form_class = FormRegistrarPaciente
    success_url = 'usuario/index_medico'
    model = Paciente
    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class})

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
            )
            user_group = Group.objects.get(name='Paciente')
            user_paciente.groups.add(user_group)
            form.id_usuario_paciente_id = user_paciente.id
            form.save()

            context = {
                'nombre_medico': user.username,
                'correo': form.email,
                'password': clave
            }

            mail = EnviarMail(context=context, recipient=form.email)
            mail.enviar()
            return redirect('index_medico',)

        except Exception as e:
            print(e.args)
            return redirect('registrar_paciente')
    
        return redirect('index_medico')
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        print(form.errors)
        return redirect('index_medico')

class VerPaciente(MedicoUserMixin, View):
    template_name = 'ver_paciente.html'
    def get(self, request, **kwargs):
        id_paciente = kwargs['pk']
        paciente = Paciente.objects.get(id = id_paciente)
        user_medico = self.request.user
        if paciente.id_medico_id == user_medico.id:
            antecedentes = AntecedentesPaciente.objects.filter(id_paciente = paciente.id)
            imagenes = Imagen.objects.filter(id_paciente = paciente.id).all()
            analisis = Analisis.objects.filter(id_imagen__in = imagenes).all()
            informes = Informe.objects.filter(id_paciente = paciente.id).all()
            antecedentesID = AntecedentesID.objects.all()
            lista_antecedentes = list(zip(antecedentesID, antecedentes))
            return render(request, self.template_name, {'paciente': paciente, 'antecedentes': lista_antecedentes, 'analisis': analisis, 'informes': informes})
        else:
            return redirect('index_medico')
        
class EditarPaciente(MedicoUserMixin, UpdateView):
    template_name = 'registrar_paciente.html'
    form_class = FormRegistrarPaciente
    model = Paciente
    pk_url_kwarg = 'pk'
    
    def form_valid(self, form_class):
        form = form_class.save()
        pk = form.id_usuario_paciente_id
        user_paciente = User.objects.get(id = pk)
        user_paciente.email = form.email
        user_paciente.save()
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return reverse('ver_paciente', args=[pk])

class RegistrarAntecedentes(MedicoUserMixin, FormView):
    template_name = 'registrar_antecedentes.html'
    form_class = AntecedentesForm
    def get(self, request, **kwargs):
        id_paciente = kwargs['pk']
        paciente = Paciente.objects.get(id=id_paciente)
        return render(request, self.template_name, {'form': self.form_class, 'paciente': paciente})

    def post(self, request, **kwargs):
        form = AntecedentesForm(request.POST)
        id_paciente = request.POST.get('pk')
        paciente = Paciente.objects.get(id=id_paciente)
        if form.is_valid():
            antecedentesID = list(AntecedentesID.objects.all())
            data = [
                form.cleaned_data['medicos'],
                form.cleaned_data['quirurgicos'],
                form.cleaned_data['alergologicos'],
                form.cleaned_data['cardiovasculares'],
                form.cleaned_data['sociales'],
                form.cleaned_data['familiares'],
                form.cleaned_data['vacunacion']
            ]
            bulk_list = []
            for indice, antecedente in enumerate(antecedentesID):
                bulk_list.append(AntecedentesPaciente(
                    id_antecedentesID=antecedente, 
                    antecedente_descrip=data[indice], 
                    id_paciente=paciente))
            AntecedentesPaciente.objects.bulk_create(bulk_list)
                
            return redirect('ver_paciente', pk=id_paciente)
        else:
            print('ERRORES DEL FORM: ')
            print(form.errors)
            return redirect('registrar_antecedentes', pk=id_paciente)
   

class RegistrarAnalisis(MedicoUserMixin, FormView):
    template_name = 'registrar_analisis.html'
    def get(self, request, **kwargs):
        id_paciente = kwargs['pk']
        paciente = Paciente.objects.get(id=id_paciente)
        return render(request, self.template_name, {'paciente': paciente}) 

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

class RegistrarInforme(MedicoUserMixin, FormView):
    template_name = 'registrar_informe.html'
    form_class = InformeForm
    model = Informe
    def get(self, request, **kwargs):
        id_paciente = kwargs.get('pk')
        paciente = Paciente.objects.get(id=id_paciente)
        img = Imagen.objects.filter(id_paciente_id = id_paciente).all()
        analisis = Analisis.objects.filter(id_imagen__in = img).all()
        return render(request, self.template_name, {'form': self.form_class, 'paciente': paciente, 'analisis': analisis})


    def form_valid(self, form_class):
        form = form_class.save(commit=False)            
        id_paciente = self.request.POST.get('pk')
        user_medico = self.request.user
        form.id_medico_id = user_medico.id
        form.id_paciente_id = id_paciente
        form.save()
        return redirect('ver_paciente', pk=id_paciente)

class EditarAntecedentes(MedicoUserMixin, FormView):
    template_name = 'registrar_antecedentes.html'
    form_class = AntecedentesForm
    
    def get(self, request, **kwargs):
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

    def post(self, request, **kwargs):
        form = self.form_class(request.POST)
        id_paciente = request.POST.get('pk')
        if form.is_valid():
            paciente = Paciente.objects.get(id=id_paciente)
            antecedentes_paciente = AntecedentesPaciente.objects.filter(id_paciente=paciente.id).all() #Antecedentes del paciente
            data = [
                form.cleaned_data['medicos'],
                form.cleaned_data['quirurgicos'],
                form.cleaned_data['alergologicos'],
                form.cleaned_data['cardiovasculares'],
                form.cleaned_data['sociales'],
                form.cleaned_data['familiares'],
                form.cleaned_data['vacunacion']
            ]
            for indice, descrip in enumerate(antecedentes_paciente):
                descrip.antecedente_descrip = antecedente_descrip=data[indice]
                descrip.save()
            return redirect('ver_paciente', pk=id_paciente)
        
        else:
            return redirect('index_paciente', pk=id_paciente)

class BusquedaView(MedicoUserMixin, ListView):
    model = Paciente
    template_name = 'index_medico.html'
    context_object_name = 'pacientes'
    
    def get_queryset(self):
        filtro = self.request.GET.get('filtro')
        datos = self.request.GET.get('datos')

        if filtro == 'nombre':
            return Paciente.objects.filter(id_medico = self.request.user.id, nombre__icontains=datos).all()

        elif filtro == 'cedula':
            return Paciente.objects.filter(
                id_medico = self.request.user.id, cedula__contains=datos).all()
        

        return Paciente.objects.filter(
                id_medico = self.request.user.id, 
                apellido__icontains=datos).all()
class EstadisticasView(MedicoUserMixin, TemplateView):
    template_name = 'estadisticas_pacientes.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hombres'] = Paciente.objects.filter(id_medico=self.request.user.id, sexo='H').count()
        context['mujeres'] = Paciente.objects.filter(id_medico=self.request.user.id, sexo='M').count()
        return context
    
class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('login')

