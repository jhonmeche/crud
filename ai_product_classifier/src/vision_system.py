"""
Sistema de Visión Artificial
Maneja la captura, procesamiento y análisis de imágenes en tiempo real
"""

import cv2
import numpy as np
from ultralytics import YOLO
import logging
from datetime import datetime
import os
from pathlib import Path

class VisionSystem:
    """
    Sistema de visión artificial para captura y procesamiento de imágenes
    Integra detección de objetos y preprocesamiento para clasificación
    """
    
    def __init__(self, camera_id=0, yolo_model_path=None):
        self.camera_id = camera_id
        self.logger = logging.getLogger(__name__)
        
        # Configuración de cámara
        self.cap = None
        self.is_camera_active = False
        
        # Configuración de procesamiento
        self.frame_width = 640
        self.frame_height = 480
        self.fps = 30
        
        # Cargar modelo YOLO para detección de objetos
        try:
            if yolo_model_path and os.path.exists(yolo_model_path):
                self.yolo_model = YOLO(yolo_model_path)
            else:
                # Usar modelo pre-entrenado
                self.yolo_model = YOLO('yolov8n.pt')  # Nano version para velocidad
            self.logger.info("Modelo YOLO cargado correctamente")
        except Exception as e:
            self.logger.warning(f"No se pudo cargar YOLO: {e}")
            self.yolo_model = None
        
        # Configuración de filtros y mejoras
        self.filters_enabled = True
        self.auto_enhance = True
        
        self.logger.info("VisionSystem inicializado")
    
    def initialize_camera(self, camera_id=None):
        """
        Inicializar cámara
        
        Args:
            camera_id: ID de la cámara (opcional)
        """
        try:
            if camera_id is not None:
                self.camera_id = camera_id
            
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                raise ValueError(f"No se pudo abrir la cámara {self.camera_id}")
            
            # Configurar propiedades de la cámara
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            self.is_camera_active = True
            self.logger.info(f"Cámara {self.camera_id} inicializada correctamente")
            
        except Exception as e:
            self.logger.error(f"Error inicializando cámara: {e}")
            self.is_camera_active = False
            raise
    
    def capture_frame(self):
        """
        Capturar un frame de la cámara
        
        Returns:
            Tuple (success, frame) donde success es bool y frame es la imagen
        """
        if not self.is_camera_active or self.cap is None:
            return False, None
        
        try:
            ret, frame = self.cap.read()
            if ret and self.auto_enhance:
                frame = self.enhance_image(frame)
            return ret, frame
        except Exception as e:
            self.logger.error(f"Error capturando frame: {e}")
            return False, None
    
    def enhance_image(self, img):
        """
        Mejorar calidad de imagen
        
        Args:
            img: Imagen de entrada
            
        Returns:
            Imagen mejorada
        """
        try:
            # Mejorar contraste y brillo
            enhanced = cv2.convertScaleAbs(img, alpha=1.2, beta=10)
            
            # Reducir ruido
            denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            # Mejorar nitidez
            kernel = np.array([[-1,-1,-1],
                              [-1, 9,-1],
                              [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            
            return sharpened
            
        except Exception as e:
            self.logger.warning(f"Error mejorando imagen: {e}")
            return img
    
    def detect_objects(self, img, confidence_threshold=0.5):
        """
        Detectar objetos en la imagen usando YOLO
        
        Args:
            img: Imagen de entrada
            confidence_threshold: Umbral de confianza para detecciones
            
        Returns:
            Lista de objetos detectados con coordenadas y confianza
        """
        if self.yolo_model is None:
            return []
        
        try:
            results = self.yolo_model(img, conf=confidence_threshold, verbose=False)
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        class_name = self.yolo_model.names[class_id]
                        
                        detections.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(confidence),
                            'class_id': class_id,
                            'class_name': class_name,
                            'area': (x2 - x1) * (y2 - y1)
                        })
            
            # Ordenar por confianza descendente
            detections.sort(key=lambda x: x['confidence'], reverse=True)
            return detections
            
        except Exception as e:
            self.logger.error(f"Error en detección de objetos: {e}")
            return []
    
    def extract_product_regions(self, img, detections=None):
        """
        Extraer regiones de productos detectados
        
        Args:
            img: Imagen original
            detections: Lista de detecciones (opcional, se calculará si no se proporciona)
            
        Returns:
            Lista de imágenes recortadas de productos
        """
        if detections is None:
            detections = self.detect_objects(img)
        
        product_regions = []
        
        for detection in detections:
            try:
                x1, y1, x2, y2 = detection['bbox']
                
                # Agregar margen para mejor contexto
                margin = 10
                x1 = max(0, x1 - margin)
                y1 = max(0, y1 - margin)
                x2 = min(img.shape[1], x2 + margin)
                y2 = min(img.shape[0], y2 + margin)
                
                # Extraer región
                region = img[y1:y2, x1:x2]
                
                if region.size > 0:
                    product_regions.append({
                        'image': region,
                        'bbox': [x1, y1, x2, y2],
                        'detection_info': detection
                    })
                    
            except Exception as e:
                self.logger.warning(f"Error extrayendo región: {e}")
                continue
        
        return product_regions
    
    def process_frame(self, frame, classify_products=False):
        """
        Procesar un frame completo
        
        Args:
            frame: Frame de entrada
            classify_products: Si clasificar productos detectados
            
        Returns:
            Diccionario con resultados del procesamiento
        """
        try:
            # Detectar objetos
            detections = self.detect_objects(frame)
            
            # Extraer regiones de productos
            product_regions = self.extract_product_regions(frame, detections)
            
            # Dibujar detecciones en el frame
            annotated_frame = self.draw_detections(frame.copy(), detections)
            
            results = {
                'frame_processed': annotated_frame,
                'detections': detections,
                'product_regions': product_regions,
                'timestamp': datetime.now().isoformat(),
                'total_objects': len(detections)
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error procesando frame: {e}")
            return {
                'frame_processed': frame,
                'detections': [],
                'product_regions': [],
                'error': str(e)
            }
    
    def draw_detections(self, img, detections):
        """
        Dibujar detecciones en la imagen
        
        Args:
            img: Imagen base
            detections: Lista de detecciones
            
        Returns:
            Imagen con detecciones dibujadas
        """
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            class_name = detection['class_name']
            
            # Dibujar rectángulo
            color = (0, 255, 0)  # Verde
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            
            # Dibujar etiqueta
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(img, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(img, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return img
    
    def save_image(self, img, filename=None, output_dir="captured_images"):
        """
        Guardar imagen capturada
        
        Args:
            img: Imagen a guardar
            filename: Nombre del archivo (opcional)
            output_dir: Directorio de salida
            
        Returns:
            Ruta del archivo guardado
        """
        try:
            # Crear directorio si no existe
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Generar nombre si no se proporciona
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"captured_{timestamp}.jpg"
            
            # Ruta completa
            file_path = os.path.join(output_dir, filename)
            
            # Guardar imagen
            cv2.imwrite(file_path, img)
            self.logger.info(f"Imagen guardada: {file_path}")
            
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error guardando imagen: {e}")
            return None
    
    def release_camera(self):
        """Liberar recursos de la cámara"""
        try:
            if self.cap is not None:
                self.cap.release()
                self.is_camera_active = False
                self.logger.info("Cámara liberada")
        except Exception as e:
            self.logger.error(f"Error liberando cámara: {e}")
    
    def get_camera_info(self):
        """Obtener información de la cámara"""
        if not self.is_camera_active or self.cap is None:
            return None
        
        try:
            info = {
                'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': int(self.cap.get(cv2.CAP_PROP_FPS)),
                'backend': self.cap.getBackendName()
            }
            return info
        except Exception as e:
            self.logger.error(f"Error obteniendo info de cámara: {e}")
            return None
    
    def adjust_camera_settings(self, width=None, height=None, fps=None):
        """
        Ajustar configuraciones de la cámara
        
        Args:
            width: Ancho del frame
            height: Alto del frame
            fps: Frames por segundo
        """
        if not self.is_camera_active or self.cap is None:
            return False
        
        try:
            if width is not None:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.frame_width = width
                
            if height is not None:
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                self.frame_height = height
                
            if fps is not None:
                self.cap.set(cv2.CAP_PROP_FPS, fps)
                self.fps = fps
            
            self.logger.info("Configuraciones de cámara actualizadas")
            return True
            
        except Exception as e:
            self.logger.error(f"Error ajustando configuraciones: {e}")
            return False
    
    def __del__(self):
        """Destructor para limpiar recursos"""
        self.release_camera()