"""
Utilidades del Sistema de Clasificación de Productos
Funciones auxiliares para logging, configuración y manejo de archivos
"""

import logging
import os
import json
from pathlib import Path
from datetime import datetime
import shutil

def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Configurar sistema de logging
    
    Args:
        log_level: Nivel de logging
        log_file: Archivo de log (opcional)
    """
    # Crear directorio de logs si es necesario
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Configurar formato
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configurar handlers
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    # Configurar logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers,
        force=True
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Sistema de logging configurado")

def create_directories():
    """Crear directorios necesarios para el proyecto"""
    directories = [
        'data/input',
        'data/output',
        'data/models',
        'data/images',
        'logs',
        'config',
        'temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(__name__)
    logger.info("Directorios del proyecto creados")

def load_config(config_path, default_config=None):
    """
    Cargar configuración desde archivo JSON
    
    Args:
        config_path: Ruta del archivo de configuración
        default_config: Configuración por defecto
        
    Returns:
        Diccionario con configuración
    """
    logger = logging.getLogger(__name__)
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"Configuración cargada desde {config_path}")
            return config
        else:
            logger.warning(f"Archivo de configuración no encontrado: {config_path}")
            return default_config or {}
    except Exception as e:
        logger.error(f"Error cargando configuración: {e}")
        return default_config or {}

def save_config(config, config_path):
    """
    Guardar configuración en archivo JSON
    
    Args:
        config: Diccionario con configuración
        config_path: Ruta donde guardar
        
    Returns:
        True si se guardó correctamente
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Crear directorio si no existe
        config_dir = os.path.dirname(config_path)
        if config_dir:
            Path(config_dir).mkdir(parents=True, exist_ok=True)
        
        # Guardar configuración
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Configuración guardada en {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error guardando configuración: {e}")
        return False

def get_file_size(file_path):
    """
    Obtener tamaño de archivo en bytes
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        Tamaño en bytes o -1 si hay error
    """
    try:
        return os.path.getsize(file_path)
    except:
        return -1

def format_file_size(size_bytes):
    """
    Formatear tamaño de archivo en formato legible
    
    Args:
        size_bytes: Tamaño en bytes
        
    Returns:
        String formateado
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"

def clean_temp_files(temp_dir='temp', max_age_hours=24):
    """
    Limpiar archivos temporales antiguos
    
    Args:
        temp_dir: Directorio de archivos temporales
        max_age_hours: Edad máxima en horas
    """
    logger = logging.getLogger(__name__)
    
    try:
        if not os.path.exists(temp_dir):
            return
        
        now = datetime.now()
        files_removed = 0
        
        for file_path in Path(temp_dir).rglob('*'):
            if file_path.is_file():
                file_age = now - datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age.total_seconds() > max_age_hours * 3600:
                    file_path.unlink()
                    files_removed += 1
        
        if files_removed > 0:
            logger.info(f"Limpiados {files_removed} archivos temporales")
            
    except Exception as e:
        logger.error(f"Error limpiando archivos temporales: {e}")

def backup_file(file_path, backup_dir='backups'):
    """
    Crear backup de un archivo
    
    Args:
        file_path: Ruta del archivo a respaldar
        backup_dir: Directorio de backups
        
    Returns:
        Ruta del backup creado o None si hay error
    """
    logger = logging.getLogger(__name__)
    
    try:
        if not os.path.exists(file_path):
            return None
        
        # Crear directorio de backup
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de backup con timestamp
        file_name = Path(file_path).name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{timestamp}_{file_name}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        # Copiar archivo
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backup creado: {backup_path}")
        
        return backup_path
        
    except Exception as e:
        logger.error(f"Error creando backup: {e}")
        return None

def validate_image_file(file_path):
    """
    Validar que un archivo sea una imagen válida
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        True si es imagen válida
    """
    try:
        import cv2
        img = cv2.imread(str(file_path))
        return img is not None
    except:
        return False

def get_supported_image_formats():
    """
    Obtener formatos de imagen soportados
    
    Returns:
        Lista de extensiones soportadas
    """
    return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']

def is_csv_file(file_path):
    """
    Verificar si un archivo es CSV
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        True si es CSV
    """
    return str(file_path).lower().endswith('.csv')

def generate_unique_filename(base_name, directory, extension=''):
    """
    Generar nombre de archivo único
    
    Args:
        base_name: Nombre base del archivo
        directory: Directorio donde se guardará
        extension: Extensión del archivo
        
    Returns:
        Nombre de archivo único
    """
    counter = 1
    original_name = f"{base_name}{extension}"
    file_path = os.path.join(directory, original_name)
    
    while os.path.exists(file_path):
        new_name = f"{base_name}_{counter}{extension}"
        file_path = os.path.join(directory, new_name)
        counter += 1
    
    return os.path.basename(file_path)

def get_project_info():
    """
    Obtener información del proyecto
    
    Returns:
        Diccionario con información del proyecto
    """
    return {
        'name': 'Sistema de Clasificación de Productos IA',
        'version': '1.0.0',
        'description': 'Software de visión artificial para clasificación de productos alimenticios',
        'author': 'AI Assistant',
        'created': datetime.now().isoformat(),
        'features': [
            'Clasificación automática de productos',
            'Procesamiento de pedidos CSV',
            'Interfaz web intuitiva',
            'Integración con cámara en tiempo real',
            'Reportes y estadísticas'
        ]
    }

def create_sample_csv(output_path):
    """
    Crear archivo CSV de ejemplo para pedidos
    
    Args:
        output_path: Ruta donde crear el archivo
        
    Returns:
        True si se creó correctamente
    """
    logger = logging.getLogger(__name__)
    
    try:
        import pandas as pd
        
        # Datos de ejemplo
        sample_data = [
            {
                'producto': 'Chocolate Snickers',
                'cantidad': 50,
                'cliente': 'Tienda ABC',
                'categoria': 'golosinas',
                'fecha_entrega': '2024-01-15',
                'urgencia': 'media'
            },
            {
                'producto': 'Atún enlatado',
                'cantidad': 30,
                'cliente': 'Supermercado XYZ',
                'categoria': 'enlatados',
                'fecha_entrega': '2024-01-14',
                'urgencia': 'alta'
            },
            {
                'producto': 'Coca Cola 2L',
                'cantidad': 24,
                'cliente': 'Restaurante DEF',
                'categoria': 'bebidas',
                'fecha_entrega': '2024-01-16',
                'urgencia': 'baja'
            },
            {
                'producto': 'Papas fritas Lays',
                'cantidad': 40,
                'cliente': 'Tienda GHI',
                'categoria': 'snacks',
                'fecha_entrega': '2024-01-13',
                'urgencia': 'urgente'
            }
        ]
        
        df = pd.DataFrame(sample_data)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        logger.info(f"CSV de ejemplo creado en {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creando CSV de ejemplo: {e}")
        return False

def check_system_requirements():
    """
    Verificar requisitos del sistema
    
    Returns:
        Diccionario con estado de requisitos
    """
    requirements = {
        'python_version': None,
        'opencv': False,
        'tensorflow': False,
        'pandas': False,
        'streamlit': False,
        'ultralytics': False,
        'all_satisfied': False
    }
    
    try:
        import sys
        requirements['python_version'] = sys.version
        
        try:
            import cv2
            requirements['opencv'] = True
        except ImportError:
            pass
        
        try:
            import tensorflow
            requirements['tensorflow'] = True
        except ImportError:
            pass
        
        try:
            import pandas
            requirements['pandas'] = True
        except ImportError:
            pass
        
        try:
            import streamlit
            requirements['streamlit'] = True
        except ImportError:
            pass
        
        try:
            import ultralytics
            requirements['ultralytics'] = True
        except ImportError:
            pass
        
        # Verificar si todos los requisitos están satisfechos
        required_packages = ['opencv', 'tensorflow', 'pandas', 'streamlit']
        requirements['all_satisfied'] = all(requirements[pkg] for pkg in required_packages)
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error verificando requisitos: {e}")
    
    return requirements