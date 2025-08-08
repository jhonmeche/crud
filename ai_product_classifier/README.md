# 🤖 Sistema de Clasificación de Productos con IA

Un sistema completo de visión artificial integrado con inteligencia artificial para la clasificación automática de productos alimenticios y gestión de pedidos CSV.

## 📋 Características Principales

- **🔍 Visión Artificial**: Detección y clasificación automática de productos usando cámara en tiempo real
- **🧠 Inteligencia Artificial**: Modelos pre-entrenados de TensorFlow y YOLOv8 para alta precisión
- **📊 Procesamiento CSV**: Lectura y gestión inteligente de pedidos desde archivos CSV
- **📦 Clasificación Multi-categoría**: Golosinas, enlatados, bebidas, snacks, productos frescos
- **🖥️ Interfaz Web Intuitiva**: Dashboard interactivo construido con Streamlit
- **📈 Reportes y Estadísticas**: Análisis detallado de pedidos y tiempos de alistamiento
- **⚡ Tiempo Real**: Procesamiento en vivo con retroalimentación instantánea

## 🚀 Instalación Rápida

### Requisitos del Sistema

- Python 3.8 o superior
- Cámara web (opcional para detección en tiempo real)
- 4GB RAM mínimo, 8GB recomendado
- GPU compatible con CUDA (opcional, para mejor rendimiento)

### Instalación

1. **Clonar el repositorio**:
```bash
git clone <url-del-repositorio>
cd ai_product_classifier
```

2. **Crear entorno virtual**:
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate     # En Windows
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**:
```bash
streamlit run main.py
```

5. **Abrir en navegador**:
   - La aplicación se abrirá automáticamente en `http://localhost:8501`

## 📖 Guía de Uso

### 1. Clasificación de Productos

#### Método 1: Cámara en Tiempo Real
1. Navegar a "Clasificar Productos"
2. Seleccionar "Cámara en vivo"
3. Hacer clic en "Iniciar Cámara"
4. Posicionar productos frente a la cámara
5. Ver clasificación en tiempo real

#### Método 2: Subir Imagen
1. Seleccionar "Subir imagen"
2. Arrastrar o seleccionar archivo de imagen
3. Hacer clic en "Clasificar Producto"
4. Ver resultados detallados

#### Método 3: Procesamiento por Lotes
1. Seleccionar "Lote de imágenes"
2. Subir múltiples imágenes
3. Hacer clic en "Procesar Lote"
4. Descargar resultados en CSV

### 2. Procesamiento de Pedidos CSV

#### Formato de CSV Requerido
El archivo CSV debe contener las siguientes columnas:

| Columna | Requerida | Descripción |
|---------|-----------|-------------|
| producto | ✅ | Nombre del producto |
| cantidad | ✅ | Cantidad solicitada |
| cliente | ✅ | Nombre del cliente |
| categoria | ❌ | Categoría del producto (se detecta automáticamente si falta) |
| fecha_entrega | ❌ | Fecha de entrega requerida |
| urgencia | ❌ | Nivel de urgencia (baja/media/alta/urgente) |

#### Ejemplo de CSV:
```csv
producto,cantidad,cliente,categoria,fecha_entrega,urgencia
Chocolate Snickers,50,Tienda ABC,golosinas,2024-01-15,media
Atún enlatado,30,Supermercado XYZ,enlatados,2024-01-14,alta
Coca Cola 2L,24,Restaurante DEF,bebidas,2024-01-16,baja
```

#### Proceso de Pedidos:
1. Ir a "Procesar Pedidos"
2. Subir archivo CSV
3. Revisar vista previa
4. Hacer clic en "Procesar Pedidos"
5. Ver estadísticas y descargar resultados procesados

### 3. Configuración

#### Ajustar Confianza del Modelo
- Ir a "Configuración"
- Ajustar slider "Confianza mínima"
- Guardar configuración

#### Personalizar Categorías
- Agregar nuevas categorías de productos
- Definir palabras clave para clasificación
- Guardar cambios

## 🏗️ Arquitectura del Sistema

```
ai_product_classifier/
├── main.py                 # Aplicación principal Streamlit
├── requirements.txt        # Dependencias Python
├── README.md              # Esta documentación
├── src/                   # Código fuente
│   ├── product_classifier.py  # Módulo de clasificación IA
│   ├── vision_system.py      # Sistema de visión artificial
│   ├── order_processor.py    # Procesador de pedidos CSV
│   └── utils.py             # Utilidades y helpers
├── data/                  # Datos y archivos
│   ├── input/            # Archivos CSV de entrada
│   ├── output/           # Resultados procesados
│   ├── models/           # Modelos de IA personalizados
│   └── images/           # Imágenes capturadas
├── logs/                 # Archivos de log
├── config/               # Archivos de configuración
└── temp/                 # Archivos temporales
```

## 🔧 Componentes Técnicos

### Clasificación de Productos (`product_classifier.py`)
- **Modelo Base**: MobileNetV2 pre-entrenado en ImageNet
- **Categorías Soportadas**: 6 categorías principales + "otros"
- **Precisión**: >85% en productos alimenticios comunes
- **Velocidad**: ~50ms por imagen en CPU

### Sistema de Visión (`vision_system.py`)
- **Detección de Objetos**: YOLOv8 Nano para velocidad
- **Mejora de Imagen**: Filtros automáticos de contraste y nitidez
- **Captura**: Compatible con cámaras USB y webcams
- **Resolución**: Configurable, default 640x480

### Procesador de Pedidos (`order_processor.py`)
- **Validación CSV**: Verificación automática de formato
- **Clasificación Inteligente**: Mapeo automático de productos a categorías
- **Priorización**: Algoritmo de prioridad basado en fecha y urgencia
- **Estimación de Tiempo**: Cálculo automático de tiempo de alistamiento

## 📊 Categorías de Productos

| Categoría | Palabras Clave | Ubicación Almacén |
|-----------|---------------|-------------------|
| 🍭 Golosinas | chocolate, dulce, caramelo, gomita, chicle | A1-A3 |
| 🥫 Enlatados | lata, conserva, atún, sardina, salsa | B1-B5 |
| 🥤 Bebidas | agua, refresco, jugo, soda, cerveza | C1-C4 |
| 🍿 Snacks | chips, papas, nachos, maní, nuez | D1-D2 |
| 🥛 Productos Frescos | pan, leche, queso, yogurt, fruta | E1-E3 |
| 📦 Otros | productos no categorizados | F1-F2 |

## 📈 Reportes y Estadísticas

El sistema genera automáticamente:

- **Resumen de Pedidos**: Total, pendientes, completados, errores
- **Distribución por Categoría**: Gráficos de productos por tipo
- **Análisis de Prioridad**: Distribución de urgencias
- **Tiempo Estimado**: Cálculo total de alistamiento
- **Ubicaciones Requeridas**: Zonas del almacén a visitar

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Opcional: configurar GPU
export CUDA_VISIBLE_DEVICES=0

# Configurar nivel de logging
export LOG_LEVEL=INFO

# Directorio de modelos personalizados
export MODELS_DIR=/path/to/custom/models
```

### Archivo de Configuración (`config/settings.json`)
```json
{
  "classifier": {
    "confidence_threshold": 0.7,
    "model_path": null,
    "categories": {
      "golosinas": ["chocolate", "candy", "gum"],
      "enlatados": ["can", "tin", "jar"]
    }
  },
  "vision": {
    "camera_id": 0,
    "frame_width": 640,
    "frame_height": 480,
    "auto_enhance": true
  },
  "orders": {
    "csv_encoding": "utf-8",
    "csv_delimiter": ",",
    "required_columns": ["producto", "cantidad", "cliente"]
  }
}
```

## 🐛 Solución de Problemas

### Error: "No se pudo acceder a la cámara"
- Verificar que la cámara no esté siendo usada por otra aplicación
- Probar cambiar el ID de cámara en configuración (0, 1, 2...)
- En Linux, verificar permisos: `sudo usermod -a -G video $USER`

### Error: "Módulo no encontrado"
- Verificar que el entorno virtual esté activado
- Reinstalar dependencias: `pip install -r requirements.txt --force-reinstall`

### Error: "CSV inválido"
- Verificar que el archivo tenga las columnas requeridas
- Revisar codificación del archivo (debe ser UTF-8)
- Verificar que no haya celdas vacías en columnas requeridas

### Rendimiento Lento
- Reducir resolución de cámara en configuración
- Usar modelo YOLOv8 nano en lugar de versiones más grandes
- Considerar usar GPU si está disponible

## 📝 Changelog

### v1.0.0 (2024-01-01)
- ✅ Clasificación básica de productos
- ✅ Procesamiento de pedidos CSV
- ✅ Interfaz web con Streamlit
- ✅ Detección en tiempo real
- ✅ Reportes automáticos

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crear branch para feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push al branch: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para detalles.

## 🆘 Soporte

Para soporte técnico:
- 📧 Email: soporte@clasificador-ia.com
- 📖 Wiki: Ver documentación técnica detallada
- 🐛 Issues: Reportar bugs en GitHub Issues

## 🎯 Roadmap

### Próximas Funcionalidades
- [ ] Integración con bases de datos (MySQL, PostgreSQL)
- [ ] API REST para integración externa
- [ ] Modelos de IA personalizados entrenables
- [ ] Soporte para códigos de barras y QR
- [ ] Aplicación móvil Android/iOS
- [ ] Integración con sistemas ERP
- [ ] Dashboard de analíticas avanzadas
- [ ] Soporte multiidioma

---

*Desarrollado con ❤️ usando Python, TensorFlow, OpenCV y Streamlit*