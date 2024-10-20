from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView, ListView
from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse

class InicioView(TemplateView):
    template_name = 'inicio.html'
