#!/usr/bin/env python3
"""
Script de Ejecución Principal
Sistema de Clasificación de Productos con IA
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Agregar directorio actual al path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Importar utilidades
try:
    from src.utils import setup_logging, create_directories, check_system_requirements, get_project_info
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrate de tener todas las dependencias instaladas: pip install -r requirements.txt")
    sys.exit(1)

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas"""
    requirements = check_system_requirements()
    
    print("🔍 Verificando requisitos del sistema...")
    print(f"Python: {requirements['python_version']}")
    
    missing_packages = []
    for package in ['opencv', 'tensorflow', 'pandas', 'streamlit']:
        status = "✅" if requirements[package] else "❌"
        print(f"{package}: {status}")
        if not requirements[package]:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Faltan paquetes: {', '.join(missing_packages)}")
        print("Instala las dependencias con: pip install -r requirements.txt")
        return False
    
    print("\n✅ Todos los requisitos están satisfechos")
    return True

def setup_environment():
    """Configurar el entorno de ejecución"""
    print("🔧 Configurando entorno...")
    
    # Configurar logging
    setup_logging(log_file="logs/app.log")
    
    # Crear directorios necesarios
    create_directories()
    
    # Verificar archivo de configuración
    config_path = current_dir / "config" / "settings.json"
    if not config_path.exists():
        print(f"⚠️  Archivo de configuración no encontrado: {config_path}")
        print("Usando configuración por defecto")
    
    print("✅ Entorno configurado correctamente")

def show_project_info():
    """Mostrar información del proyecto"""
    info = get_project_info()
    
    print("=" * 60)
    print(f"🤖 {info['name']}")
    print(f"📝 Versión: {info['version']}")
    print(f"📄 {info['description']}")
    print("=" * 60)
    
    print("\n📋 Características:")
    for feature in info['features']:
        print(f"   • {feature}")
    
    print("\n🌐 La aplicación se abrirá en: http://localhost:8501")
    print("💡 Presiona Ctrl+C para detener la aplicación")
    print("=" * 60)

def run_streamlit():
    """Ejecutar la aplicación Streamlit"""
    main_script = current_dir / "main.py"
    
    if not main_script.exists():
        print(f"❌ No se encontró el archivo principal: {main_script}")
        return False
    
    try:
        print("\n🚀 Iniciando aplicación...")
        
        # Configurar variables de entorno para Streamlit
        env = os.environ.copy()
        env['STREAMLIT_SERVER_PORT'] = '8501'
        env['STREAMLIT_SERVER_ADDRESS'] = 'localhost'
        env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        
        # Ejecutar Streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", str(main_script)]
        subprocess.run(cmd, env=env, cwd=str(current_dir))
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️  Aplicación detenida por el usuario")
        return True
    except Exception as e:
        print(f"❌ Error ejecutando la aplicación: {e}")
        return False

def main():
    """Función principal"""
    try:
        # Mostrar información del proyecto
        show_project_info()
        
        # Verificar dependencias
        if not check_dependencies():
            return 1
        
        # Configurar entorno
        setup_environment()
        
        # Ejecutar aplicación
        if run_streamlit():
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Ejecución cancelada por el usuario")
        return 0
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())