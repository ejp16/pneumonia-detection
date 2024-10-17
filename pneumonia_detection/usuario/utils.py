import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
from keras.models import load_model
import numpy as np
import cv2
from django.conf import settings
import google.generativeai as genai
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags


class Modelo:
    def __init__(self, imagen):
        self.imagen = 'C:/Users/usuario/Desktop/Eduardo/sistema_tesis/pneumonia_detection'+imagen
        self.prob = 0
        self.clase = ''
    def prediccion(self):
        modelo = load_model('C:/Users/usuario/Desktop/Eduardo/sistema_tesis/pneumonia_detection/modelo.keras')
        carga = cv2.resize(cv2.imread(self.imagen, 3), (160,160))
        carga = carga.reshape((160, 160, 3))
        prediccion = modelo.predict(carga)
        if prediccion[0][0] > prediccion[0][1]:
            self.clase = 'normal'
            self.prob = prediccion[0][0] 
        else: 
            self.clase = 'neumonia'
            self.prob = prediccion[0][1]
        
        return {'resultado': self.clase, 'probabilidad': round(self.prob, 2)}

    def prompt(self, edad, peso, altura, antecedentes):
        texto = (f"Paciente de {edad} años de edad con peso de {peso} "
        f"y altura de {altura} cm, con los siguientes antecedentes. "
        f"Medicos: {antecedentes[0].antecedente_descrip} "
        f"Quirurgicos: {antecedentes[1].antecedente_descrip} "
        f"Alergologicos: {antecedentes[2].antecedente_descrip} "
        f"Cardiovasculares: {antecedentes[3].antecedente_descrip} "
        f"Sociales: {antecedentes[4].antecedente_descrip} "
        f"Familiares: {antecedentes[5].antecedente_descrip} "
        f"Vacunacion: {antecedentes[6].antecedente_descrip} "
        
        f"Una red neuronal de alta precision analizo una radiografia de torax de este paciente "
        f"dando como resultado {self.clase} con una probabilidad de {self.prob}. "

        "Escribe las recomendaciones generales que deberia seguir el paciente en menos de 1100 caracteres"
        "No utilizar tildes ni acentos durante la respuesta"

        )
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            texto,
        )

        return response.text
            
class EnviarMail:
    def __init__(self, context, recipient):
        self.context = context
        self.recipient = recipient
    def enviar(self):
        template_name = 'correo.html'
        convert_to_html_content = render_to_string(
            template_name=template_name,
            context=self.context
        )
        print(self.recipient)
        plain_message = strip_tags(convert_to_html_content)
        send_mail(
            subject='Contraseña del sistema',
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.recipient],
            html_message=convert_to_html_content,
            fail_silently=True
        )
