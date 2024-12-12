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
from xhtml2pdf import pisa
from django.template.loader import get_template
from io import BytesIO
from django.http import HttpResponse


class Modelo:
    def __init__(self, imagen):
        self.imagen = '../pneumonia_detection'+imagen
        self.prob = 0
        self.clase = ''
    def prediccion(self):
        modelo = load_model('modelo.keras')
        carga = cv2.resize(cv2.imread(self.imagen, 3), (160,160))
        carga = carga.reshape((160, 160, 3))
        prediccion = modelo.predict(carga)
        if prediccion[0][0] > prediccion[0][1]:
            self.clase = 'Normal'
            self.prob = prediccion[0][0] 
        else: 
            self.clase = 'Neumonía'
            self.prob = prediccion[0][1] 
        return {'resultado': self.clase, 'probabilidad': round(self.prob*100, 2)}

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

        )
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            texto,
        )

        return response.text
            

def enviar_email(context, recipient, template, asunto):
    template_name = template
    convert_to_html_content = render_to_string(
        template_name=template_name,
        context=context
    )
    print(recipient)
    plain_message = strip_tags(convert_to_html_content)
    send_mail(
        subject=asunto,
        message=plain_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[recipient],
        html_message=convert_to_html_content,
        fail_silently=True
    )

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('utf-8')), result)
    if not pdf.err: 
        return HttpResponse(result.getvalue(), content_type='application/pdf') 
    else:
        return None
