from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView
from django.views import View
from django.shortcuts import render
from .models import Usuario, Analisis, Imagenes, HistoriaPaciente
from django.contrib import messages
from django.shortcuts import redirect
from .forms import RegistroForm, LoginForm, HistoriaPacientes
from .utils import Modelo

class RegisterView(CreateView):
    template_name = 'registro.html'
    form_class = RegistroForm
    success_url = '/usuario/login'
    model = Usuario()
    def form_valid(self, form_class):
        form_class.save()
        return super().form_valid(form_class)
    
class LoginView(View):
    template_name = "login.html"
    form_class = LoginForm()
    def get(self, request):
        if 'email' not in request.session:
            return render(request, self.template_name, {'form': self.form_class})
        else:
            return redirect('home')

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = Usuario.objects.filter(email=email).first()
            if user and user.password == password:
                request.session['email'] = email
                return redirect('home')
            else:
                messages.warning(request, 'Correo o contraseña incorrectos')
            return redirect('login')

class HomeView(View):
    template_name = 'home.html'
    def get(self, request):
        if 'email' in request.session:
            email = request.session.get('email')
            user = Usuario.objects.filter(email=email).first()
            print(f'Usuario: {user}')
            historias = HistoriaPaciente.objects.filter(id_usuario = user.id).all()
            analisis = Analisis.objects.filter(id_usuario = user.id).all()
            print(analisis)
            return render(request, self.template_name, {'historias': historias, 'analisis': analisis})
        else:
            return redirect('login')

class RegistrarHistoria(View):
    template_name = 'registrar_historia.html'
    form_class = HistoriaPacientes()  

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request, **kwargs):
        form = HistoriaPacientes(request.POST)
        if form.is_valid():
            email = request.session.get('email')
            user = Usuario.objects.filter(email=email).first()
            print(form.cleaned_data['nombre_paciente'])
            HistoriaPaciente(
                nombre_paciente=form.cleaned_data['nombre_paciente'],
                edad=form.cleaned_data['edad'],
                cedula=form.cleaned_data['cedula'],
                telefono=form.cleaned_data['telefono'],
                email_paciente=form.cleaned_data['email_paciente'],
                observaciones=form.cleaned_data['observaciones'],
                id_usuario=user,
            ).save()
            return redirect('home')
        else:
            return redirect('registrar_paciente')

class RegistrarAnalisisView(FormView):
    template_name = 'registrar_analisis.html'
    def get(self, request):
        email = request.session['email']
        usuario = Usuario.objects.filter(email = email).first()
        pacientes = HistoriaPaciente.objects.filter(id_usuario = usuario).all()
        context = {'pacientes': pacientes}
        return render(request, self.template_name, context)
    
    def post(self, request):
        imagen = request.FILES['radiografia']
        email = request.session.get('email')
        paciente = request.POST.get('paciente')
        historia = HistoriaPaciente.objects.get(id=paciente)
        Imagenes(imagen = imagen, id_Hpaciente=historia).save()
        img = Imagenes.objects.all().last()
        img_url = img.imagen.url
        modelo = Modelo(img_url)
        respuesta = modelo.prediccion()
        Analisis(
            resultado=respuesta['resultado'],
            probabilidad=respuesta['probabilidad'],
            recomendaciones='lol',
            id_imagen=img
        ).save()
        return redirect('home')

class VerHistoria(TemplateView):
    template_name = 'ver_historia.html'
    def get(self, request, **kwargs):
        usuario = Usuario.objects.filter(email=request.session.get('email')).first()
        id = kwargs['id']
        paciente = HistoriaPaciente.objects.get(id=id)
        print(paciente.id_usuario_id)
        print(usuario.id)
        if paciente.id_usuario_id == usuario.id:
            img = Imagenes.objects.filter(id_Hpaciente = paciente.id).first()
            if img: 
                analisis = Analisis.objects.filter(id_imagen = img.id).first()
                return render(request, self.template_name, {'paciente': paciente, 'analisis': analisis, 'img': img.imagen})
            else:
                return render(request, self.template_name, {'paciente': paciente, 'analisis': False})
 
        else:
            return redirect('home')

class EditarHistoria(UpdateView):
    model = HistoriaPaciente
    template_name = 'registrar_historia.html'
    form_class = HistoriaPacientes
    success_url = '/usuario/home'

class BorrarHistoria(DeleteView):
    model = HistoriaPaciente
    success_url = '/home'
    template_name = 'eliminar_paciente.html'

class Logout(View):
    def get(self, request):
        request.session.pop('email')
        return redirect('login')
