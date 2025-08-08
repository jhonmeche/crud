"""
Módulo de Clasificación de Productos
Utiliza modelos de deep learning para clasificar productos alimenticios
"""

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import pickle
import os
from pathlib import Path
import logging

class ProductClassifier:
    """
    Clasificador de productos usando visión artificial e IA
    Especializado en productos alimenticios: golosinas, enlatados, etc.
    """
    
    def __init__(self, model_path=None, confidence_threshold=0.7):
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)
        
        # Categorías de productos específicas
        self.product_categories = {
            'golosinas': ['chocolate', 'candy', 'gum', 'lollipop', 'cookie', 'cake'],
            'enlatados': ['can', 'tin', 'jar', 'bottle', 'container'],
            'bebidas': ['bottle', 'can', 'drink', 'soda', 'juice', 'water'],
            'snacks': ['chips', 'crackers', 'nuts', 'popcorn'],
            'productos_frescos': ['fruit', 'vegetable', 'bread', 'dairy'],
            'otros': []
        }
        
        # Cargar o inicializar modelo
        if model_path and os.path.exists(model_path):
            self.load_custom_model(model_path)
        else:
            self.load_pretrained_model()
            
        self.logger.info("ProductClassifier inicializado correctamente")
    
    def load_pretrained_model(self):
        """Cargar modelo pre-entrenado MobileNetV2"""
        try:
            self.model = MobileNetV2(weights='imagenet', include_top=True)
            self.model_type = 'pretrained'
            self.logger.info("Modelo MobileNetV2 pre-entrenado cargado")
        except Exception as e:
            self.logger.error(f"Error cargando modelo pre-entrenado: {e}")
            raise
    
    def load_custom_model(self, model_path):
        """Cargar modelo personalizado entrenado"""
        try:
            self.model = tf.keras.models.load_model(model_path)
            self.model_type = 'custom'
            self.logger.info(f"Modelo personalizado cargado desde {model_path}")
        except Exception as e:
            self.logger.error(f"Error cargando modelo personalizado: {e}")
            self.load_pretrained_model()  # Fallback al modelo pre-entrenado
    
    def preprocess_image(self, img, target_size=(224, 224)):
        """
        Preprocesar imagen para el modelo
        
        Args:
            img: Imagen en formato OpenCV (BGR)
            target_size: Tamaño objetivo para el modelo
            
        Returns:
            Imagen preprocesada para predicción
        """
        # Convertir BGR a RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Redimensionar
        img_resized = cv2.resize(img_rgb, target_size)
        
        # Expandir dimensiones para batch
        img_array = np.expand_dims(img_resized, axis=0)
        
        # Preprocesar según el modelo
        if self.model_type == 'pretrained':
            img_preprocessed = preprocess_input(img_array)
        else:
            img_preprocessed = img_array.astype('float32') / 255.0
            
        return img_preprocessed
    
    def classify_image(self, img):
        """
        Clasificar una imagen de producto
        
        Args:
            img: Imagen en formato OpenCV (BGR)
            
        Returns:
            Diccionario con resultados de clasificación
        """
        try:
            # Preprocesar imagen
            processed_img = self.preprocess_image(img)
            
            # Realizar predicción
            predictions = self.model.predict(processed_img, verbose=0)
            
            # Procesar resultados según tipo de modelo
            if self.model_type == 'pretrained':
                results = self._process_pretrained_predictions(predictions)
            else:
                results = self._process_custom_predictions(predictions)
                
            # Agregar información adicional
            results.update({
                'image_shape': img.shape,
                'model_type': self.model_type,
                'confidence_threshold': self.confidence_threshold
            })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error en clasificación: {e}")
            return {
                'error': str(e),
                'categoria': 'error',
                'confianza': 0.0,
                'predicciones': []
            }
    
    def _process_pretrained_predictions(self, predictions):
        """Procesar predicciones del modelo pre-entrenado"""
        # Decodificar predicciones de ImageNet
        decoded_predictions = decode_predictions(predictions, top=5)[0]
        
        # Mapear a nuestras categorías
        categoria_detectada = 'otros'
        max_confidence = 0.0
        predicciones_mapeadas = []
        
        for class_id, label, confidence in decoded_predictions:
            # Mapear label a nuestras categorías
            categoria = self._map_imagenet_to_category(label.lower())
            predicciones_mapeadas.append({
                'label': label,
                'categoria': categoria,
                'confianza': float(confidence)
            })
            
            # Actualizar categoría principal si es más confiable
            if confidence > max_confidence and categoria != 'otros':
                categoria_detectada = categoria
                max_confidence = float(confidence)
        
        return {
            'categoria': categoria_detectada,
            'confianza': max_confidence,
            'predicciones': predicciones_mapeadas,
            'cumple_threshold': max_confidence >= self.confidence_threshold
        }
    
    def _process_custom_predictions(self, predictions):
        """Procesar predicciones del modelo personalizado"""
        # Obtener índice de la clase con mayor probabilidad
        predicted_class = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class])
        
        # Mapear índice a categoría (esto dependería del entrenamiento)
        categories = list(self.product_categories.keys())
        categoria = categories[predicted_class] if predicted_class < len(categories) else 'otros'
        
        return {
            'categoria': categoria,
            'confianza': confidence,
            'predicciones': [{'categoria': categoria, 'confianza': confidence}],
            'cumple_threshold': confidence >= self.confidence_threshold
        }
    
    def _map_imagenet_to_category(self, imagenet_label):
        """
        Mapear etiquetas de ImageNet a nuestras categorías de productos
        
        Args:
            imagenet_label: Etiqueta de ImageNet en minúsculas
            
        Returns:
            Categoría mapeada
        """
        for categoria, keywords in self.product_categories.items():
            for keyword in keywords:
                if keyword in imagenet_label:
                    return categoria
        
        # Mapeos específicos adicionales
        if any(word in imagenet_label for word in ['preserves', 'jam', 'soup']):
            return 'enlatados'
        elif any(word in imagenet_label for word in ['beer', 'wine', 'cocktail']):
            return 'bebidas'
        elif any(word in imagenet_label for word in ['pizza', 'hamburger', 'hotdog']):
            return 'snacks'
        
        return 'otros'
    
    def detect_multiple_products(self, img):
        """
        Detectar múltiples productos en una imagen usando YOLO
        
        Args:
            img: Imagen en formato OpenCV (BGR)
            
        Returns:
            Lista de productos detectados con sus ubicaciones
        """
        try:
            # Aquí se podría integrar YOLOv5 para detección de objetos
            # Por ahora, clasificamos la imagen completa
            classification_result = self.classify_image(img)
            
            return [{
                'bbox': [0, 0, img.shape[1], img.shape[0]],  # Imagen completa
                'classification': classification_result
            }]
            
        except Exception as e:
            self.logger.error(f"Error en detección múltiple: {e}")
            return []
    
    def update_confidence_threshold(self, new_threshold):
        """Actualizar umbral de confianza"""
        self.confidence_threshold = max(0.1, min(1.0, new_threshold))
        self.logger.info(f"Umbral de confianza actualizado a {self.confidence_threshold}")
    
    def get_supported_categories(self):
        """Obtener lista de categorías soportadas"""
        return list(self.product_categories.keys())
    
    def add_custom_category(self, category_name, keywords):
        """
        Agregar nueva categoría personalizada
        
        Args:
            category_name: Nombre de la nueva categoría
            keywords: Lista de palabras clave para mapeo
        """
        self.product_categories[category_name] = keywords
        self.logger.info(f"Categoría '{category_name}' agregada con keywords: {keywords}")
    
    def save_classification_results(self, results, output_path):
        """Guardar resultados de clasificación"""
        try:
            with open(output_path, 'wb') as f:
                pickle.dump(results, f)
            self.logger.info(f"Resultados guardados en {output_path}")
        except Exception as e:
            self.logger.error(f"Error guardando resultados: {e}")