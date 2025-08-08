# 🚀 Guía de Instalación Paso a Paso

Esta guía te ayudará a instalar y configurar el Sistema de Clasificación de Productos con IA en tu sistema.

## 📋 Requisitos Previos

### Sistema Operativo
- **Windows**: Windows 10 o superior
- **macOS**: macOS 10.14 o superior  
- **Linux**: Ubuntu 18.04+ / CentOS 7+ / Debian 9+

### Hardware
- **RAM**: Mínimo 4GB, recomendado 8GB
- **Espacio en disco**: Mínimo 2GB libres
- **Cámara web**: Opcional para detección en tiempo real
- **GPU**: Opcional, compatible con CUDA para mejor rendimiento

### Software
- **Python**: Versión 3.8 - 3.11 (recomendado 3.9)
- **pip**: Incluido con Python
- **Git**: Para clonar el repositorio

## 🔧 Instalación

### Paso 1: Verificar Python

Abre una terminal/consola y verifica que Python esté instalado:

```bash
python --version
# o si usas python3
python3 --version
```

**Resultado esperado**: `Python 3.8.x` o superior

**Si no tienes Python instalado:**

#### Windows:
1. Descargar desde [python.org](https://www.python.org/downloads/windows/)
2. **IMPORTANTE**: Marcar "Add Python to PATH" durante la instalación
3. Reiniciar la terminal después de instalar

#### macOS:
```bash
# Opción 1: Homebrew (recomendado)
brew install python

# Opción 2: Descargar desde python.org
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### Linux (CentOS/RHEL):
```bash
sudo yum install python3 python3-pip
# o en sistemas más nuevos:
sudo dnf install python3 python3-pip
```

### Paso 2: Descargar el Proyecto

#### Opción A: Clonar con Git (recomendado)
```bash
git clone <url-del-repositorio>
cd ai_product_classifier
```

#### Opción B: Descargar ZIP
1. Descargar el archivo ZIP del proyecto
2. Extraer en la carpeta deseada
3. Abrir terminal en esa carpeta

### Paso 3: Crear Entorno Virtual

Es **altamente recomendado** usar un entorno virtual:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual

# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate
```

**Verificar activación**: El prompt debería mostrar `(venv)` al inicio.

### Paso 4: Instalar Dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias del proyecto
pip install -r requirements.txt
```

**Este proceso puede tomar 5-15 minutos** dependiendo de tu conexión a internet.

### Paso 5: Verificar Instalación

Ejecuta el script de verificación:

```bash
python run.py
```

Si todo está correcto, verás:
- ✅ Verificación de requisitos exitosa
- 🔧 Configuración del entorno
- 🚀 Inicio de la aplicación

## 🐛 Solución de Problemas Comunes

### Error: "python: command not found"

**En Windows:**
```bash
# Usar py en lugar de python
py --version
py -m venv venv
py -m pip install -r requirements.txt
```

**En macOS/Linux:**
```bash
# Usar python3 explícitamente
python3 --version
python3 -m venv venv
python3 -m pip install -r requirements.txt
```

### Error: "Permission denied" (Linux/macOS)

```bash
# Dar permisos de ejecución
chmod +x run.py

# O ejecutar con python
python run.py
```

### Error: "pip: command not found"

**Windows:**
```bash
py -m ensurepip --upgrade
```

**macOS:**
```bash
# Instalar pip con Homebrew
brew install python
# o descargar get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install python3-pip

# CentOS/RHEL
sudo yum install python3-pip
```

### Error: "Microsoft Visual C++ 14.0 is required" (Windows)

Instalar Visual Studio Build Tools:
1. Descargar [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019)
2. Instalar con las herramientas de C++
3. Reiniciar y volver a ejecutar `pip install -r requirements.txt`

### Error: "Failed building wheel for opencv-python"

**Solución 1**: Instalar versión específica
```bash
pip install opencv-python-headless==4.8.1.78
```

**Solución 2**: Usar conda (si tienes Anaconda)
```bash
conda install opencv
```

**Solución 3**: Instalar dependencias del sistema (Linux)
```bash
# Ubuntu/Debian
sudo apt install libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1-mesa-glx

# CentOS/RHEL
sudo yum install glib2-devel libSM libXext libXrender mesa-libGL
```

### Error: "Cannot import tensorflow"

**Si tienes GPU NVIDIA:**
```bash
# Desinstalar CPU version
pip uninstall tensorflow

# Instalar GPU version
pip install tensorflow-gpu==2.13.0
```

**Si solo tienes CPU:**
```bash
# Reinstalar versión CPU
pip uninstall tensorflow
pip install tensorflow-cpu==2.13.0
```

### Error: "Streamlit command not found"

```bash
# Verificar instalación
pip list | grep streamlit

# Si no aparece, reinstalar
pip install streamlit==1.26.0

# Ejecutar directamente
python -m streamlit run main.py
```

### Error: "No se pudo acceder a la cámara"

**Windows:**
1. Verificar que ninguna otra aplicación use la cámara
2. Ir a Configuración → Privacidad → Cámara → Permitir aplicaciones de escritorio

**macOS:**
1. Sistema → Preferencias → Seguridad → Privacidad → Cámara
2. Permitir Terminal o la aplicación que ejecute Python

**Linux:**
```bash
# Verificar dispositivos de cámara
ls /dev/video*

# Agregar usuario al grupo video
sudo usermod -a -G video $USER

# Reiniciar sesión
```

## ⚡ Instalación Rápida (Una Línea)

Para usuarios avanzados con Git y Python ya instalados:

```bash
git clone <url-repo> && cd ai_product_classifier && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python run.py
```

**Windows:**
```cmd
git clone <url-repo> && cd ai_product_classifier && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python run.py
```

## 🔄 Actualización

Para actualizar a una nueva versión:

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate     # Windows

# Actualizar código
git pull origin main

# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Ejecutar
python run.py
```

## 🗑️ Desinstalación

Para remover completamente el proyecto:

```bash
# Desactivar entorno virtual
deactivate

# Eliminar carpeta del proyecto
rm -rf ai_product_classifier  # Linux/macOS
# o
rmdir /s ai_product_classifier  # Windows
```

## 🆘 Obtener Ayuda

Si sigues teniendo problemas:

1. **Verificar logs**: Revisar archivos en `logs/app.log`
2. **Issues en GitHub**: Reportar problemas específicos
3. **Documentación**: Consultar `README.md` para más detalles
4. **Comunidad**: Buscar soluciones en foros de Python/TensorFlow

## ✅ Próximos Pasos

Una vez instalado exitosamente:

1. **Explorar la interfaz**: Navegar por las diferentes secciones
2. **Probar con datos de ejemplo**: Usar `data/sample_orders.csv`
3. **Configurar tu cámara**: Ajustar configuraciones en la sección correspondiente
4. **Personalizar categorías**: Adaptar a tus tipos de productos específicos

¡Felicidades! Ya tienes el Sistema de Clasificación de Productos con IA funcionando. 🎉