"""
Procesador de Pedidos
Maneja la lectura, procesamiento y gestión de pedidos en formato CSV
Integra con el sistema de clasificación para alistamiento automático
"""

import pandas as pd
import numpy as np
import csv
import logging
from datetime import datetime, timedelta
from pathlib import Path
import os
import json

class OrderProcessor:
    """
    Procesador de pedidos CSV con integración de clasificación de productos
    """
    
    def __init__(self, config_path=None):
        self.logger = logging.getLogger(__name__)
        
        # Configuración por defecto
        self.default_config = {
            'csv_encoding': 'utf-8',
            'csv_delimiter': ',',
            'required_columns': ['producto', 'cantidad', 'cliente'],
            'optional_columns': ['categoria', 'precio', 'fecha_entrega', 'urgencia'],
            'status_values': ['pendiente', 'alistando', 'completado', 'cancelado'],
            'priority_levels': ['baja', 'media', 'alta', 'urgente']
        }
        
        # Cargar configuración
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
        else:
            self.config = self.default_config.copy()
        
        # Inventario y categorías
        self.inventory = {}
        self.product_categories = {
            'golosinas': [],
            'enlatados': [],
            'bebidas': [],
            'snacks': [],
            'productos_frescos': [],
            'otros': []
        }
        
        # Estadísticas
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'errors': 0,
            'last_update': None
        }
        
        self.logger.info("OrderProcessor inicializado")
    
    def load_config(self, config_path):
        """Cargar configuración desde archivo JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.config = {**self.default_config, **config}
            self.logger.info(f"Configuración cargada desde {config_path}")
        except Exception as e:
            self.logger.error(f"Error cargando configuración: {e}")
            self.config = self.default_config.copy()
    
    def validate_csv_format(self, df):
        """
        Validar formato del CSV de pedidos
        
        Args:
            df: DataFrame con los datos del CSV
            
        Returns:
            Tuple (is_valid, errors)
        """
        errors = []
        
        # Verificar columnas requeridas
        for col in self.config['required_columns']:
            if col not in df.columns:
                errors.append(f"Columna requerida faltante: {col}")
        
        # Verificar datos mínimos
        if df.empty:
            errors.append("El archivo CSV está vacío")
        
        # Verificar tipos de datos básicos
        if 'cantidad' in df.columns:
            non_numeric = df[~pd.to_numeric(df['cantidad'], errors='coerce').notna()]
            if not non_numeric.empty:
                errors.append(f"Valores no numéricos en columna 'cantidad': {len(non_numeric)} filas")
        
        return len(errors) == 0, errors
    
    def read_csv_orders(self, file_path, validate=True):
        """
        Leer pedidos desde archivo CSV
        
        Args:
            file_path: Ruta del archivo CSV
            validate: Si validar el formato
            
        Returns:
            DataFrame con los pedidos o None si hay error
        """
        try:
            # Leer CSV con configuración
            df = pd.read_csv(
                file_path,
                encoding=self.config['csv_encoding'],
                delimiter=self.config['csv_delimiter']
            )
            
            self.logger.info(f"CSV leído: {len(df)} filas, {len(df.columns)} columnas")
            
            # Validar si se solicita
            if validate:
                is_valid, errors = self.validate_csv_format(df)
                if not is_valid:
                    self.logger.error(f"CSV inválido: {errors}")
                    return None
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error leyendo CSV: {e}")
            return None
    
    def process_orders(self, df_orders):
        """
        Procesar DataFrame de pedidos
        
        Args:
            df_orders: DataFrame con pedidos
            
        Returns:
            DataFrame procesado con información adicional
        """
        try:
            df_processed = df_orders.copy()
            
            # Agregar columnas de procesamiento
            df_processed['estado'] = 'pendiente'
            df_processed['fecha_procesamiento'] = datetime.now()
            df_processed['prioridad'] = 'media'
            df_processed['categoria_detectada'] = 'sin_clasificar'
            df_processed['confianza_clasificacion'] = 0.0
            df_processed['ubicacion_almacen'] = ''
            df_processed['tiempo_estimado_alistamiento'] = 0
            
            # Procesar cada pedido
            for idx, row in df_processed.iterrows():
                try:
                    # Clasificar producto si no tiene categoría
                    if pd.isna(row.get('categoria', np.nan)):
                        categoria = self._classify_product_name(row['producto'])
                        df_processed.at[idx, 'categoria_detectada'] = categoria
                    else:
                        df_processed.at[idx, 'categoria_detectada'] = row['categoria']
                    
                    # Calcular prioridad
                    prioridad = self._calculate_priority(row)
                    df_processed.at[idx, 'prioridad'] = prioridad
                    
                    # Verificar inventario
                    disponible = self._check_inventory(row['producto'], row['cantidad'])
                    if not disponible:
                        df_processed.at[idx, 'estado'] = 'sin_stock'
                    
                    # Estimar tiempo de alistamiento
                    tiempo_estimado = self._estimate_fulfillment_time(row)
                    df_processed.at[idx, 'tiempo_estimado_alistamiento'] = tiempo_estimado
                    
                    # Asignar ubicación en almacén
                    ubicacion = self._get_storage_location(df_processed.at[idx, 'categoria_detectada'])
                    df_processed.at[idx, 'ubicacion_almacen'] = ubicacion
                    
                except Exception as e:
                    self.logger.warning(f"Error procesando fila {idx}: {e}")
                    df_processed.at[idx, 'estado'] = 'error'
            
            # Ordenar por prioridad y fecha
            priority_order = {'urgente': 0, 'alta': 1, 'media': 2, 'baja': 3}
            df_processed['priority_num'] = df_processed['prioridad'].map(priority_order)
            df_processed = df_processed.sort_values(['priority_num', 'fecha_procesamiento'])
            df_processed.drop('priority_num', axis=1, inplace=True)
            
            # Actualizar estadísticas
            self._update_processing_stats(df_processed)
            
            self.logger.info(f"Procesados {len(df_processed)} pedidos")
            return df_processed
            
        except Exception as e:
            self.logger.error(f"Error procesando pedidos: {e}")
            return df_orders
    
    def _classify_product_name(self, product_name):
        """
        Clasificar producto basado en su nombre
        
        Args:
            product_name: Nombre del producto
            
        Returns:
            Categoría detectada
        """
        product_lower = product_name.lower()
        
        # Palabras clave para cada categoría
        category_keywords = {
            'golosinas': ['chocolate', 'dulce', 'caramelo', 'gomita', 'chicle', 'paleta', 'galleta'],
            'enlatados': ['lata', 'conserva', 'enlatado', 'atún', 'sardina', 'salsa', 'mermelada'],
            'bebidas': ['agua', 'refresco', 'jugo', 'soda', 'cerveza', 'vino', 'café', 'té'],
            'snacks': ['chips', 'papas', 'nachos', 'maní', 'nuez', 'almendra', 'mix'],
            'productos_frescos': ['pan', 'leche', 'queso', 'yogurt', 'fruta', 'verdura', 'carne']
        }
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in product_lower:
                    return category
        
        return 'otros'
    
    def _calculate_priority(self, order_row):
        """
        Calcular prioridad del pedido
        
        Args:
            order_row: Fila del pedido
            
        Returns:
            Nivel de prioridad
        """
        # Prioridad base
        priority = 'media'
        
        # Verificar si hay columna de urgencia
        if 'urgencia' in order_row and pd.notna(order_row['urgencia']):
            urgencia = str(order_row['urgencia']).lower()
            if urgencia in ['urgente', 'alta', 'media', 'baja']:
                priority = urgencia
        
        # Verificar fecha de entrega
        if 'fecha_entrega' in order_row and pd.notna(order_row['fecha_entrega']):
            try:
                fecha_entrega = pd.to_datetime(order_row['fecha_entrega'])
                dias_restantes = (fecha_entrega - datetime.now()).days
                
                if dias_restantes <= 1:
                    priority = 'urgente'
                elif dias_restantes <= 3:
                    priority = 'alta'
                elif dias_restantes <= 7:
                    priority = 'media'
                else:
                    priority = 'baja'
            except:
                pass
        
        # Verificar cantidad (pedidos grandes tienen mayor prioridad)
        if 'cantidad' in order_row and pd.notna(order_row['cantidad']):
            try:
                cantidad = float(order_row['cantidad'])
                if cantidad >= 100 and priority == 'baja':
                    priority = 'media'
                elif cantidad >= 500 and priority == 'media':
                    priority = 'alta'
            except:
                pass
        
        return priority
    
    def _check_inventory(self, product_name, quantity):
        """
        Verificar disponibilidad en inventario
        
        Args:
            product_name: Nombre del producto
            quantity: Cantidad solicitada
            
        Returns:
            True si hay stock suficiente
        """
        # Por ahora simular inventario
        # En implementación real se conectaría a base de datos
        if product_name not in self.inventory:
            # Asumir stock disponible para productos nuevos
            return True
        
        available = self.inventory.get(product_name, 0)
        return available >= quantity
    
    def _estimate_fulfillment_time(self, order_row):
        """
        Estimar tiempo de alistamiento en minutos
        
        Args:
            order_row: Fila del pedido
            
        Returns:
            Tiempo estimado en minutos
        """
        # Tiempo base por categoría (minutos)
        category_times = {
            'golosinas': 5,
            'enlatados': 3,
            'bebidas': 4,
            'snacks': 6,
            'productos_frescos': 8,
            'otros': 7
        }
        
        categoria = order_row.get('categoria_detectada', 'otros')
        base_time = category_times.get(categoria, 7)
        
        # Ajustar por cantidad
        try:
            cantidad = float(order_row.get('cantidad', 1))
            # Tiempo adicional por cada 10 unidades
            additional_time = (cantidad // 10) * 2
            total_time = base_time + additional_time
        except:
            total_time = base_time
        
        return min(total_time, 60)  # Máximo 60 minutos
    
    def _get_storage_location(self, category):
        """
        Obtener ubicación en almacén según categoría
        
        Args:
            category: Categoría del producto
            
        Returns:
            Código de ubicación
        """
        locations = {
            'golosinas': 'A1-A3',
            'enlatados': 'B1-B5',
            'bebidas': 'C1-C4',
            'snacks': 'D1-D2',
            'productos_frescos': 'E1-E3',
            'otros': 'F1-F2'
        }
        
        return locations.get(category, 'F1-F2')
    
    def _update_processing_stats(self, df_processed):
        """Actualizar estadísticas de procesamiento"""
        self.processing_stats['total_processed'] += len(df_processed)
        self.processing_stats['successful'] += len(df_processed[df_processed['estado'] != 'error'])
        self.processing_stats['errors'] += len(df_processed[df_processed['estado'] == 'error'])
        self.processing_stats['last_update'] = datetime.now()
    
    def create_fulfillment_report(self, df_orders):
        """
        Crear reporte de alistamiento
        
        Args:
            df_orders: DataFrame con pedidos procesados
            
        Returns:
            Diccionario con reporte detallado
        """
        try:
            report = {
                'resumen': {
                    'total_pedidos': len(df_orders),
                    'pendientes': len(df_orders[df_orders['estado'] == 'pendiente']),
                    'alistando': len(df_orders[df_orders['estado'] == 'alistando']),
                    'completados': len(df_orders[df_orders['estado'] == 'completado']),
                    'sin_stock': len(df_orders[df_orders['estado'] == 'sin_stock']),
                    'errors': len(df_orders[df_orders['estado'] == 'error'])
                },
                'por_categoria': df_orders['categoria_detectada'].value_counts().to_dict(),
                'por_prioridad': df_orders['prioridad'].value_counts().to_dict(),
                'tiempo_total_estimado': df_orders['tiempo_estimado_alistamiento'].sum(),
                'ubicaciones_requeridas': df_orders['ubicacion_almacen'].unique().tolist(),
                'fecha_reporte': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error creando reporte: {e}")
            return {}
    
    def export_processed_orders(self, df_orders, output_path, format='csv'):
        """
        Exportar pedidos procesados
        
        Args:
            df_orders: DataFrame con pedidos
            output_path: Ruta de salida
            format: Formato de exportación ('csv', 'excel', 'json')
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if format.lower() == 'csv':
                df_orders.to_csv(output_path, index=False, encoding='utf-8')
            elif format.lower() == 'excel':
                df_orders.to_excel(output_path, index=False)
            elif format.lower() == 'json':
                df_orders.to_json(output_path, orient='records', date_format='iso')
            else:
                raise ValueError(f"Formato no soportado: {format}")
            
            self.logger.info(f"Pedidos exportados a {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exportando pedidos: {e}")
            return False
    
    def get_statistics(self):
        """Obtener estadísticas del procesador"""
        return self.processing_stats.copy()
    
    def update_inventory(self, inventory_dict):
        """
        Actualizar inventario
        
        Args:
            inventory_dict: Diccionario con productos y cantidades
        """
        self.inventory.update(inventory_dict)
        self.logger.info(f"Inventario actualizado: {len(inventory_dict)} productos")
    
    def load_inventory_from_csv(self, csv_path):
        """
        Cargar inventario desde CSV
        
        Args:
            csv_path: Ruta del archivo CSV de inventario
        """
        try:
            df_inventory = pd.read_csv(csv_path)
            if 'producto' in df_inventory.columns and 'cantidad' in df_inventory.columns:
                inventory_dict = dict(zip(df_inventory['producto'], df_inventory['cantidad']))
                self.update_inventory(inventory_dict)
                return True
            else:
                self.logger.error("CSV de inventario debe tener columnas 'producto' y 'cantidad'")
                return False
        except Exception as e:
            self.logger.error(f"Error cargando inventario: {e}")
            return False