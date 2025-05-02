# -*- coding: utf-8 -*-
"""
Created on Thu May  1 18:29:15 2025

@author: jahop
"""

import streamlit as st
import feedparser
import pandas as pd
import spacy
from urllib.parse import quote

# Cargar modelo de spaCy (debe estar especificado en requirements.txt)
try:
    nlp = spacy.load("es_core_news_sm")
except:
    st.error("Error al cargar el modelo de spaCy. Verifica que esté correctamente instalado.")
    st.stop()

# Lista de estados mexicanos
estados_mexicanos = [
    "Aguascalientes", "Baja California", "Baja California Sur", "Campeche", "CDMX", "Ciudad de México",
    "Chiapas", "Chihuahua", "Coahuila", "Colima", "Durango", "Estado de México", "Guanajuato", "Guerrero",
    "Hidalgo", "Jalisco", "Michoacán", "Morelos", "Nayarit", "Nuevo León", "Oaxaca", "Puebla", "Querétaro",
    "Quintana Roo", "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas", "Tlaxcala", "Veracruz",
    "Yucatán", "Zacatecas"
]

def detectar_estado(texto):
    doc = nlp(texto)
    for ent in doc.ents:
        if ent.label_ == "LOC" or ent.label_ == "GPE":
            for estado in estados_mexicanos:
                if estado.lower() in ent.text.lower():
                    return estado
    return None

def buscar_noticias_nlp(consulta):
    url = f"https://news.google.com/rss/search?q={quote(consulta)}&hl=es-419&gl=MX&ceid=MX:es-419"
    feed = feedparser.parse(url)
    
    noticias = []
    for entry in feed.entries:
        texto = entry.title + " " + entry.summary
        estado_detectado = detectar_estado(texto)
        if estado_detectado:
            noticias.append({
                "Título": entry.title,
                "Publicado": entry.published,
                "Resumen": entry.summary,
                "Estado Detectado": estado_detectado,
                "Enlace": entry.link
            })
    return pd.DataFrame(noticias)

# Interfaz en Streamlit
st.set_page_config(page_title="PROFEPA - Detección Ambiental", layout="wide")




# Sección de descarga del manual
with open("manual.pdf", "rb") as pdf_file:
    st.sidebar.download_button(
        label="📘 Descargar Manual de Usuario (PDF)",
        data=pdf_file,
        file_name="manual.pdf",
        mime="application/pdf"
    )

# Sección de Sidebar para Ayuda
st.sidebar.title("Ayuda")
st.sidebar.markdown("""
    **Aplicación de Monitor de Incidentes Ambientales en México**
    
    Esta aplicación permite realizar un análisis en tiempo real de noticias relacionadas con incidentes ambientales en México.
    
    🛠 **¿Cómo funciona?**
    - Introduce una palabra clave relacionada con incidentes ambientales (como "derrame de petróleo" o "incendio forestal") en el campo de búsqueda.
    - El sistema buscará noticias relevantes en fuentes abiertas y utilizará **Procesamiento de Lenguaje Natural (NLP)** para identificar las menciones a los **estados de México** en las noticias.
    - Se muestra un ranking con los estados con más incidentes, y podrás hacer clic en los enlaces para leer las noticias completas.

    🔍 **Objetivo de la aplicación**
    - Monitorear de manera rápida y sencilla los incidentes ambientales ocurridos en distintos estados de la República Mexicana.
    - Facilitar la toma de decisiones para acciones de prevención o mitigación a través de información en tiempo real.

    📊 **¿Qué puedes hacer?**
    - Buscar noticias en tiempo real sobre incidentes ambientales.
    - Ver el ranking de estados con más incidentes reportados.
    - Descargar los resultados en formato CSV para un análisis posterior.

    **¡Usa esta herramienta para estar informado sobre los incidentes ambientales en México!**
""")

# Título principal
st.title("🌎 PROFEPA: Monitor de Incidentes Ambientales en México (NLP)")

# Entrada de consulta
query = st.text_input("🔍 Palabra clave (ej: derrame petróleo, incendio forestal):", "incendio forestal")

if st.button("Buscar noticias"):
    with st.spinner("Buscando y analizando noticias..."):
        df = buscar_noticias_nlp(query)
        
        if not df.empty:
            # Mostrar noticias encontradas
            st.success(f"Se encontraron {len(df)} noticias relevantes.")
            st.dataframe(df)
            
            # Convertir la columna 'Enlace' en clickeable
            def make_clickable(val):
                return f'<a href="{val}" target="_blank">Abrir Noticia</a>'
            df['Enlace'] = df['Enlace'].apply(make_clickable)
            st.markdown(df.to_html(escape=False), unsafe_allow_html=True)

            # Descargar el CSV
            st.download_button("📥 Descargar CSV", df.to_csv(index=False), "noticias_nlp_mexico.csv")

            # Crear un ranking de estados con más incidentes
            estado_counts = df['Estado Detectado'].value_counts().reset_index()
            estado_counts.columns = ['Estado', 'Cantidad de Incidentes']
            st.subheader("Ranking de Estados con Más Incidentes Ambientales")
            st.dataframe(estado_counts)

            # Visualización del ranking con un gráfico de barras
            st.bar_chart(estado_counts.set_index('Estado')['Cantidad de Incidentes'])
        
        else:
            st.warning("No se encontraron noticias relevantes en México para esa palabra clave.")

# Desarrollado por: Javier Horacio Pérez Ricárdez
st.markdown("<br><hr><br>", unsafe_allow_html=True)
st.markdown("### Desarrollado por: **Javier Horacio Pérez Ricárdez**", unsafe_allow_html=True)

# También en la barra lateral
st.sidebar.markdown("### Desarrollado por: **Javier Horacio Pérez Ricárdez**")
