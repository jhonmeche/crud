#!/usr/bin/env python3
"""
Sistema de Clasificación de Productos con Visión Artificial e IA
Desarrollado para clasificar productos desde golosinas hasta enlatados
Procesa pedidos en formato CSV
"""

import streamlit as st
import pandas as pd
import cv2
import numpy as np
from pathlib import Path
import sys
import os

# Agregar el directorio actual al path para importar módulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.product_classifier import ProductClassifier
from src.order_processor import OrderProcessor
from src.vision_system import VisionSystem
from src.utils import setup_logging, create_directories

# Configuración de la aplicación
st.set_page_config(
    page_title="Sistema de Clasificación de Productos IA",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Función principal de la aplicación"""
    setup_logging()
    create_directories()
    
    st.title("🤖 Sistema de Clasificación de Productos con IA")
    st.markdown("---")
    
    # Sidebar para navegación
    st.sidebar.title("Navegación")
    option = st.sidebar.selectbox(
        "Selecciona una opción:",
        ["Inicio", "Clasificar Productos", "Procesar Pedidos", "Configuración"]
    )
    
    # Inicializar sistemas
    if 'classifier' not in st.session_state:
        st.session_state.classifier = ProductClassifier()
    if 'vision_system' not in st.session_state:
        st.session_state.vision_system = VisionSystem()
    if 'order_processor' not in st.session_state:
        st.session_state.order_processor = OrderProcessor()
    
    if option == "Inicio":
        show_home_page()
    elif option == "Clasificar Productos":
        show_classification_page()
    elif option == "Procesar Pedidos":
        show_order_processing_page()
    elif option == "Configuración":
        show_configuration_page()

def show_home_page():
    """Página de inicio con información del sistema"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("📋 Características del Sistema")
        st.write("""
        - 🔍 **Visión Artificial**: Detección y clasificación automática de productos
        - 🧠 **Inteligencia Artificial**: Modelos pre-entrenados y personalizables
        - 📊 **Procesamiento CSV**: Lectura y gestión de pedidos
        - 📦 **Clasificación Multi-categoría**: Golosinas, enlatados, y más
        - 🖥️ **Interfaz Intuitiva**: Fácil de usar y configurar
        """)
        
    with col2:
        st.header("🚀 Comenzar")
        if st.button("Clasificar Nuevos Productos", type="primary"):
            st.switch_page("pages/classifier.py")
        if st.button("Procesar Pedidos CSV"):
            st.switch_page("pages/orders.py")

def show_classification_page():
    """Página para clasificación de productos"""
    st.header("🔍 Clasificación de Productos")
    
    # Opciones de entrada
    input_option = st.radio(
        "Selecciona el método de entrada:",
        ["Cámara en vivo", "Subir imagen", "Lote de imágenes"]
    )
    
    if input_option == "Cámara en vivo":
        camera_classification()
    elif input_option == "Subir imagen":
        image_upload_classification()
    elif input_option == "Lote de imágenes":
        batch_classification()

def camera_classification():
    """Clasificación usando cámara en vivo"""
    st.subheader("📷 Clasificación en Tiempo Real")
    
    if st.button("Iniciar Cámara"):
        camera_placeholder = st.empty()
        results_placeholder = st.empty()
        
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                st.error("No se pudo acceder a la cámara")
                break
                
            # Procesar frame
            results = st.session_state.vision_system.process_frame(frame)
            
            # Mostrar frame procesado
            camera_placeholder.image(frame, channels="BGR", use_column_width=True)
            
            # Mostrar resultados
            if results:
                results_placeholder.json(results)
                
            if st.button("Detener Cámara"):
                break
                
        cap.release()

def image_upload_classification():
    """Clasificación de imagen subida"""
    st.subheader("📤 Subir Imagen para Clasificar")
    
    uploaded_file = st.file_uploader(
        "Selecciona una imagen",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        # Mostrar imagen
        image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), 1)
        st.image(image, channels="BGR", caption="Imagen subida")
        
        # Clasificar
        if st.button("Clasificar Producto"):
            with st.spinner("Procesando..."):
                results = st.session_state.classifier.classify_image(image)
                
            st.success("¡Clasificación completada!")
            st.json(results)

def batch_classification():
    """Clasificación por lotes"""
    st.subheader("📁 Clasificación por Lotes")
    
    uploaded_files = st.file_uploader(
        "Selecciona múltiples imágenes",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.write(f"Imágenes seleccionadas: {len(uploaded_files)}")
        
        if st.button("Procesar Lote"):
            progress_bar = st.progress(0)
            results_container = st.container()
            
            all_results = []
            
            for i, file in enumerate(uploaded_files):
                image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), 1)
                result = st.session_state.classifier.classify_image(image)
                result['filename'] = file.name
                all_results.append(result)
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            # Mostrar resultados
            df = pd.DataFrame(all_results)
            st.dataframe(df)
            
            # Descargar resultados
            csv = df.to_csv(index=False)
            st.download_button(
                "Descargar Resultados",
                csv,
                "clasificacion_resultados.csv",
                "text/csv"
            )

def show_order_processing_page():
    """Página para procesamiento de pedidos"""
    st.header("📊 Procesamiento de Pedidos CSV")
    
    uploaded_csv = st.file_uploader(
        "Subir archivo CSV de pedidos",
        type=['csv'],
        accept_multiple_files=False
    )
    
    if uploaded_csv is not None:
        # Leer CSV
        df = pd.read_csv(uploaded_csv)
        st.write("Vista previa del archivo:")
        st.dataframe(df.head())
        
        if st.button("Procesar Pedidos"):
            processed_orders = st.session_state.order_processor.process_orders(df)
            
            st.success("¡Pedidos procesados!")
            st.dataframe(processed_orders)
            
            # Estadísticas
            show_order_statistics(processed_orders)

def show_order_statistics(orders_df):
    """Mostrar estadísticas de pedidos"""
    st.subheader("📈 Estadísticas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Productos", len(orders_df))
    with col2:
        st.metric("Categorías Únicas", orders_df['categoria'].nunique())
    with col3:
        st.metric("Productos por Alistar", orders_df['estado'].value_counts().get('pendiente', 0))

def show_configuration_page():
    """Página de configuración"""
    st.header("⚙️ Configuración del Sistema")
    
    st.subheader("Configuración del Modelo")
    model_confidence = st.slider("Confianza mínima", 0.1, 1.0, 0.7)
    
    st.subheader("Categorías de Productos")
    categories = st.text_area(
        "Categorías (una por línea)",
        "golosinas\nenlatados\nbebidas\nsnacks\nproductos_frescos"
    )
    
    if st.button("Guardar Configuración"):
        st.success("Configuración guardada!")

if __name__ == "__main__":
    main()