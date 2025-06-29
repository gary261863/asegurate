# app_seguros.py

import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Puedes definir tus valores por defecto aquí
default_nombre = "Juan Pérez"
default_edad = 30
default_ocupacion = "Ingeniero de Software"
default_ingresos_anuales = 5000  # En BOB
default_tipo_seguro = "Vida"
default_necesidades = "Busco un seguro que cubra gastos médicos mayores y tenga opción de inversión."

# --- Definición de las funciones de cada página ---
def main_page():
    st.title("¡Bienvenido a 'Asegúrate'!")
    st.write("Descubre el seguro ideal para ti con nuestra herramienta personalizada.")
    if st.button("¿Qué seguro va conmigo?"):
        st.session_state.page = "formulario"
        st.rerun()

def form_page():
    st.title("Descubre tu Seguro Ideal")
    st.write("Por favor, introduce tus datos para ayudarte a encontrar el seguro perfecto.")

    with st.form("solicitud_seguro"):
        nombre = st.text_input("Nombre completo", value=default_nombre)
        edad = st.number_input("Edad", min_value=18, max_value=100,value=default_edad)
        ocupacion = st.text_input("Ocupación", value=default_ocupacion)
        ingresos_anuales = st.number_input("Ingresos mensuales (BOB)", min_value=0, value=default_ingresos_anuales)
        tipo_seguro_interes = st.selectbox(
            "¿En qué tipo de seguro estás interesado?",
            ["Salud", "Vida", "Automóvil", "Hogar", "Viajes", "Inversión", "Otro"]
        )
        necesidades_especificas = st.text_area("¿Hay alguna necesidad o preocupación específica que tengas sobre el seguro?", value=default_necesidades)

        submitted = st.form_submit_button("Procesar Solicitud")

        if submitted:
            st.session_state.user_data = {
                "nombre": nombre,
                "edad": edad,
                "ocupacion": ocupacion,
                "ingresos_anuales": ingresos_anuales,
                "tipo_seguro_interes": tipo_seguro_interes,
                "necesidades_especificas": necesidades_especificas
            }
            st.session_state.page = "resultado"
            st.rerun()

def result_page():
    st.title("Resultado de tu Solicitud")

    if "user_data" not in st.session_state:
        st.warning("No se encontraron datos de usuario. Por favor, regresa al formulario.")
        if st.button("Volver al formulario"):
            st.session_state.page = "formulario"
            st.rerun()
        return

    user_data = st.session_state.user_data

    # --- Carga la clave API desde el archivo .env ---
    load_dotenv() # Carga las variables de entorno del archivo .env
    gemini_api_key = os.getenv("GEMINI_API_KEY") # Obtiene la clave de la variable de entorno

    if not gemini_api_key:
        st.error("Error: La clave API de Gemini no se encontró. Asegúrate de que GEMINI_API_KEY esté en tu archivo .env.")
        st.stop() # Detiene la ejecución si no se encuentra la clave

    genai.configure(api_key=gemini_api_key) # Usa la clave cargada

    prompt = f"""
    Eres un asesor de seguros experto y amigable. Basado en los siguientes datos del usuario,
    recomienda el tipo de seguro más adecuado y explica brevemente por qué.
    También, sugiere posibles coberturas clave y consideraciones importantes.

    Datos del Usuario:
    - Nombre: {user_data['nombre']}
    - Edad: {user_data['edad']}
    - Ocupación: {user_data['ocupacion']}
    - Ingresos Anuales: ${user_data['ingresos_anuales']}
    - Tipo de Seguro de Interés: {user_data['tipo_seguro_interes']}
    - Necesidades Específicas: {user_data['necesidades_especificas'] if user_data['necesidades_especificas'] else 'Ninguna especificada'}

    Considera los siguientes puntos al generar la recomendación:
    - ¿Qué tipo de seguro se alinea mejor con su edad, ocupación e ingresos?
    - ¿Qué riesgos comunes podría enfrentar esta persona que un seguro podría mitigar?
    - Si mencionó un tipo de seguro de interés, ¿cómo podemos profundizar en eso?
    - Si tiene necesidades específicas, ¿cómo se pueden abordar?

    Formato de la respuesta:
    Recomendación de Seguro: [Tipo de Seguro Recomendado]
    Por qué este seguro es adecuado: [Explicación concisa]
    Coberturas Clave Sugeridas:
    - [Cobertura 1]
    - [Cobertura 2]
    - [Cobertura 3]
    Consideraciones Importantes: [Puntos adicionales a considerar]
    """

    model = genai.GenerativeModel('gemini-1.5-flash')

    try:
        with st.spinner("Procesando tu solicitud y obteniendo la mejor recomendación..."):
            response = model.generate_content(prompt)
            recomendacion = response.text
        st.text_area("Aquí está nuestra recomendación personalizada:", recomendacion, height=300)
    except Exception as e:
        st.error(f"Hubo un error al procesar tu solicitud: {e}")
        st.info("Por favor, asegúrate de que tu clave API de Gemini Pro sea válida y de que no haya problemas de conexión.")

    if st.button("Volver al inicio"):
        st.session_state.page = "main"
        st.rerun()


# --- Lógica de navegación principal ---
if "page" not in st.session_state:
    st.session_state.page = "main"

if st.session_state.page == "main":
    main_page()
elif st.session_state.page == "formulario":
    form_page()
elif st.session_state.page == "resultado":
    result_page()