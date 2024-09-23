import tensorflow as tf
from keras.models import load_model
import numpy as np
import cv2

class Modelo:
    def __init__(self, imagen):
        self.imagen = 'C:/Users/usuario/Desktop/Eduardo/sistema_tesis/pneumonia_detection'+imagen

    def prediccion(self):
        modelo = load_model('C:/Users/usuario/Desktop/Eduardo/sistema_tesis/pneumonia_detection/modelo.keras')
        carga = cv2.resize(cv2.imread(self.imagen, 3), (160,160))
        carga = carga.reshape((160, 160, 3))
        prediccion = modelo.predict(carga)
        print(prediccion[0])
        if prediccion[0][0] > prediccion[0][1]:
            clase = 'normal'
            prob = prediccion[0][0] 
        else: 
            clase = 'neumonia'
            prob = prediccion[0][1]

        
        return {'resultado': clase, 'probabilidad': round(prob, 2)}
