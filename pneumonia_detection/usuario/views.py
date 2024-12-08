from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView, ListView
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .backend import EmailBackend
from .models import *
from django.contrib import messages
from .forms import FormRegistro, LoginForm, AntecedentesForm, FormRegistrarPaciente, InformeForm, ImagenForm
from .utils import Modelo, enviar_email, render_to_pdf
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import UserPassesTestMixin
from datetime import datetime
from django.conf import settings
from django.core.files import File

#Validar que el usuario que ingresa a la ruta es un medico
class MedicoUserMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Medico').exists()

#Validar que el usuario que ingresa a la ruta es un paciente
class PacienteUserMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Paciente').exists()

#Vista para el registro del medico
class RegistroView(CreateView):
    template_name = 'registro.html' #Plantilla
    form_class = FormRegistro #Formulario de registro
    success_url = '/usuario/login' #Ruta a la que se redirige el usuario si el formulario es valido
    model = User 
    def form_valid(self, form_class):
        user = form_class.save(commit=False)
        group = Group.objects.get(name='Medico')
        user.save()
        user.groups.add(group)
        
        return redirect('login')

#Vista para iniciar sesion
class LoginView(View):
    template_name = "login.html" #Platilla
    form_class = LoginForm() #Formulario de login 
    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request):
        form = LoginForm(request.POST) #Carga el formulario con los datos ingresados
        if form.is_valid(): #Verificar si es valido
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
                messages.warning(request, 'Correo o contraseña incorrectos')
            return redirect('login')
        return redirect('login')

#Vista de inicio del medico 
class IndexMedicoView(MedicoUserMixin, ListView):
    template_name = 'plantillas_medico/index_medico.html'
    model = Paciente
    context_object_name = 'pacientes'
    #Metodo para obtener la informacion de la base de datos
    def get_queryset(self):
        relacion = RelacionMedicoPaciente.objects.filter(id_medico=self.request.user.id).values_list('id_paciente', flat=True)
        return Paciente.objects.filter(id__in=relacion).all()

 #Vista de inicio del paciente   
class IndexPaciente(PacienteUserMixin, ListView):
    template_name = 'plantillas_paciente/index_paciente.html'
    model = Paciente
    paginate_by = 20
    def get_context_data(self, **kwargs):
        #Metodo para obtener la informacion de la base de datos
        context = super().get_context_data(**kwargs)
        pacientes = Paciente.objects.filter(id_usuario_paciente=self.request.user.id).all()
        medicos = RelacionMedicoPaciente.objects.filter(id_paciente__in=pacientes).select_related('id_medico').all().distinct()
        context['items'] = list(zip(medicos, pacientes))
        return context

#Vista de revision de informes por parte del paciente
class MisInformes(PacienteUserMixin, TemplateView):
    template_name = 'plantillas_paciente/informes_paciente.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        pk_paciente = kwargs.get('pk_paciente')
        pk_medico = kwargs.get('pk_medico')
        context['analisis'] = Analisis.objects.select_related('id_imagen').filter(id_medico=pk_medico, id_paciente=pk_paciente).all() 
        context['informes'] = Informe.objects.filter(id_paciente=pk_paciente).all()
        return self.render_to_response(context)

class RegistrarPacienteView(MedicoUserMixin, CreateView):
    template_name = 'plantillas_medico/registrar_paciente.html'
    form_class = FormRegistrarPaciente
    success_url = 'usuario/index_medico'
    model = Paciente
    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class})
    #Metodo que solo se llamara si el formulario fue llenado correctamente
    def form_valid(self, form_class):
        paciente = form_class.save(commit=False)
        user = self.request.user
        clave = get_random_string(8) #genera la clave del paciente
        user_paciente = User.objects.filter(email=paciente.email).first() #Verifica si el email ingresado ya esta en uso por un Usuario

        #Calcular la edad del paciente
        edad = datetime.now().date() - paciente.fecha_nacimiento
        paciente.edad = edad.days//365
        
        if user_paciente:
            #Si esta en uso, crear registro en la tabla Paciente y asignar el id_usuario_paciente al Usuario ligado a ese correo
            paciente.id_usuario_paciente = user_paciente
            paciente.save()
            RelacionMedicoPaciente.objects.create(
                id_medico=self.request.user,
                id_paciente=paciente
            )
            return redirect('index_medico',)
        
        #Crear Usuario del paciente
        user_paciente = User.objects.create_user(
            username=paciente.nombre,
            email=paciente.email,
            password=clave,
        )
        #Asignarlo al grupo Pacientes y guardar los datos en la tabla Paciente
        user_group = Group.objects.get(name='Paciente')
        user_paciente.groups.add(user_group)
        paciente.id_usuario_paciente_id = user_paciente.id
        paciente.save()

        RelacionMedicoPaciente.objects.create(
            id_medico=self.request.user,
            id_paciente=paciente
        )

        #Enviar email con los datos para el inicio de sesion
        context = {
            'nombre_medico': user.username,
            'correo': paciente.email,
            'password': clave
        }

        enviar_email(context=context, 
                    recipient=paciente.email, 
                    template='correo_password.html', 
                    asunto='Contraseña del sistema Neumonet')
        
        return redirect('index_medico',)

    #Metodo que se llama si hay errores en el formulario
    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response
   
#Vista del medico para ver la informacion y analisis de un paciente
class VerPaciente(MedicoUserMixin, View):
    template_name = 'plantillas_medico/ver_paciente.html'
    def get(self, request, **kwargs):
        id_paciente = kwargs['pk']
        user_medico = self.request.user
        relacion_paciente = RelacionMedicoPaciente.objects.get(id_medico=user_medico.id, id_paciente=id_paciente)
        if relacion_paciente:
            analisis = Analisis.objects.filter(id_paciente = relacion_paciente.id_paciente).select_related('id_imagen').all()
            informes = Informe.objects.filter(id_paciente = relacion_paciente.id_paciente).all()
            antecedentes = AntecedentesPaciente.objects.filter(id_paciente = relacion_paciente.id_paciente)
            lista_antecedentes = None
            if antecedentes:
                antecedentesID = ["Médicos", "Quirúrgicos", "Alergológicos", "Cardiovasculares", "Sociales", "Familiares", "Vacunación"]
                lista_antecedentes = zip(antecedentesID, antecedentes)
            return render(request, self.template_name, {'relacion_paciente': relacion_paciente, 'antecedentes': lista_antecedentes, 'analisis': analisis, 'informes': informes})
        else:
            return redirect('index_medico')

#Vista para editar los datos personales del paciente        
class EditarPaciente(MedicoUserMixin, UpdateView):
    template_name = 'plantillas_medico/registrar_paciente.html'
    form_class = FormRegistrarPaciente
    model = Paciente
    pk_url_kwarg = 'pk'
    
    def form_valid(self, form_class):
        form = form_class.save(commit=False) #Cargar los datos en el formulario
        pk = form.id_usuario_paciente_id #Obtener el id del usuario del paciente
        user_paciente = User.objects.get(id = pk) #Obtener el usuario del paciente  
        user_paciente.email = form.email #Actualizar el correo electronico del usuario del paciente
        #Calcular la fecha de nacimiento
        edad = datetime.now().date() - form.fecha_nacimiento
        form.edad = edad.days//365
        user_paciente.save()
        return super().form_valid(form)
    #Si la accion es exitosa, redirigir a la vista del paciente
    def get_success_url(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return reverse('ver_paciente', args=[pk])

#Vista para registrar antecedentes
class RegistrarAntecedentes(MedicoUserMixin, FormView):
    template_name = 'plantillas_medico/registrar_antecedentes.html'
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
   
#Registrar analisis
class RegistrarAnalisis(MedicoUserMixin, FormView):
    template_name = 'plantillas_medico/registrar_analisis.html'
    form_class = ImagenForm

    def get(self, request, **kwargs):
        id_paciente = kwargs['pk']
        paciente = Paciente.objects.get(id=id_paciente)
        form = self.form_class
        return render(request, self.template_name, {'paciente': paciente, 'form': form}) 
    #Si el formulario es valido
    def form_valid(self, form):
        imagen = form.cleaned_data.get('image_field')
        id_paciente = self.request.POST.get('pk')
        paciente = Paciente.objects.get(id=id_paciente)
        antecedentes = list(AntecedentesPaciente.objects.filter(id_paciente = paciente.id).order_by('-id_antecedentesID'))
        if not antecedentes: 
            messages.warning(self.request, 'Debe registrar los antecedentes del paciente antes de usar la red neuronal')
            return redirect('registrar_analisis', pk=id_paciente)
        try:
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
            analisis = Analisis.objects.create(
                resultado=prediccion['resultado'],
                probabilidad=prediccion['probabilidad'],
                recomendaciones=recomendacion,
                id_imagen=img,
                id_medico=self.request.user,
                id_paciente=paciente
            )

            context = {
                'nombre_medico': analisis.id_medico.username,
                'link': f'http://127.0.0.1:8000/usuario/descargar_analisis/{analisis.id}'
            }

            enviar_email(context=context,
                        recipient=paciente.email,
                        template='correo_analisis.html',
                        asunto='Resultado de Análisis de Radiografía')
                                                
            return redirect('ver_paciente', pk=id_paciente)
        except Exception as e:
            messages.error(self.request, 'Ocurrio un error, intentalo denuevo')
            return redirect('registrar_analisis', pk=id_paciente)
#Registrar informes
class RegistrarInforme(MedicoUserMixin, FormView):
    template_name = 'plantillas_medico/registrar_informe.html'
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
    template_name = 'plantillas_medico/registrar_antecedentes.html'
    form_class = AntecedentesForm
    
    def get(self, request, **kwargs):
        id_paciente = kwargs['pk']
        paciente = Paciente.objects.get(id=id_paciente)
        id = kwargs['pk']
        #Listar los antecedentes y antecedentes id
        data = list(AntecedentesPaciente.objects.filter(id_paciente = id).order_by('-id_antecedentesID'))
        antecedentesIds = list(AntecedentesID.objects.all().order_by('-id'))
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
                descrip.antecedente_descrip = data[indice]
                descrip.save()
            return redirect('ver_paciente', pk=id_paciente)
        
        else:
            print(form.errors)
            return redirect('index_paciente', pk=id_paciente)

class BusquedaView(MedicoUserMixin, ListView):
    model = Paciente
    template_name = 'plantillas_medico/index_medico.html'
    context_object_name = 'pacientes'
    
    def get_queryset(self):
        filtro = self.request.GET.get('filtro')
        datos = self.request.GET.get('datos')
        relacion = RelacionMedicoPaciente.objects.filter(id_medico=self.request.user.id).values_list('id_paciente', flat=True)
        if filtro == 'nombre':
            return Paciente.objects.filter(id__in = relacion, nombre__icontains=datos).all()

        elif filtro == 'cedula':
            return Paciente.objects.filter(
                id__in = relacion, cedula__contains=datos).all()
        
        return Paciente.objects.filter(
                id__in = relacion,
                apellido__icontains=datos).all()

class EstadisticasView(MedicoUserMixin, View):
    template_name = 'plantillas_medico/estadisticas_pacientes.html'
    context = {}
    def get(self, request, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context=context)

    def post(self, request):
        desde = request.POST.get('desde')
        hasta = request.POST.get('hasta')
        edad_desde = request.POST.get('edad_desde')
        edad_hasta = request.POST.get('edad_hasta')
        context = self.get_context_data()
        query = RelacionMedicoPaciente.objects.filter(id_medico=self.request.user.id).values_list('id_paciente', flat=True)
        context['edad_desde'] = edad_desde
        context['edad_hasta'] = edad_hasta
        context['edades_mujeres'] = Paciente.objects.filter(id__in=query, sexo='M', edad__range=(edad_desde, edad_hasta)).count()
        context['edades_hombres'] = Paciente.objects.filter(id__in=query, sexo='H', edad__range=(edad_desde, edad_hasta)).count()
        neumonia = Analisis.objects.filter(id_paciente__in=query, fecha_analisis__range=(desde, hasta), resultado='neumonia').count()
        normal = Analisis.objects.filter(id_paciente__in=query, fecha_analisis__range=(desde, hasta), resultado='normal').count()
        context['normal'] = normal
        context['neumonia'] = neumonia
        context['desde'] = desde
        context['hasta'] = hasta
        
        return render(request, self.template_name, context=context)


    def get_context_data(self, **kwargs):
        query = RelacionMedicoPaciente.objects.filter(id_medico=self.request.user.id).values_list('id_paciente', flat=True)
        self.context['hombres'] = Paciente.objects.filter(id__in=query, sexo='H').count()
        self.context['mujeres'] = Paciente.objects.filter(id__in=query, sexo='M').count()
        
        self.context['edades_5_10'] = Paciente.objects.filter(id__in=query, edad__range=(4,11)).count()
        self.context['edades_10_20'] = Paciente.objects.filter(id__in=query, edad__range=(10,22)).count()

        return self.context 

class DescargarInforme(View):
    template_name = 'pdf_informe.html'
    
    def get(self, request, **kwargs):
        id_informe = kwargs['pk']
        informe = Informe.objects.get(id = id_informe)
        context = {
            'id': id_informe,
            'motivo_consulta': informe.motivo_consulta,
            'observaciones': informe.observaciones,
            'recomendaciones': informe.recomendaciones,
            'medicacion': informe.medicacion,
            'fecha_consulta': informe.fecha_consulta,
        }

        pdf = render_to_pdf(self.template_name, context)
        return HttpResponse(pdf, content_type='application/pdf')
    
class DescargarAnalisis(View):
    template_name = 'pdf_analisis.html'
    
    def get(self, request, **kwargs):
        id_analisis = kwargs['pk']
        analisis = Analisis.objects.get(id = id_analisis)
        imagen = Imagen.objects.get(id = analisis.id_imagen_id)
        context = {
            'id': id_analisis,
            'resultado': analisis.resultado,
            'probabilidad': analisis.probabilidad,
            'recomendaciones': analisis.recomendaciones,
            'fecha': analisis.fecha_analisis,
            'nombre_paciente': analisis.id_paciente.nombre,
            'apellido_paciente': analisis.id_paciente.apellido,
            'nombre_medico': analisis.id_medico.username,
            'img': imagen
        }

        pdf = render_to_pdf(self.template_name, context)
        return HttpResponse(pdf, content_type='application/pdf')

class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('inicio')

