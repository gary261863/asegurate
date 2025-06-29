import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
from dotenv import load_dotenv


#  # --- Carga la clave API desde el archivo .env ---
# load_dotenv() # Carga las variables de entorno del archivo .env
# gemini_api_key = os.getenv("GEMINI_API_KEY") # Obtiene la clave de la variable de entorno


# genai.configure(api_key="gemini_api_key")
# model = genai.GenerativeModel('gemini-1.5-flash')



# --- Paso 1: Cargar las variables de entorno del archivo .env ---
load_dotenv()

# --- Paso 2: Obtener la clave API de la variable de entorno ---
# Asegúrate de que el nombre de la variable aquí (ej. 'GEMINI_API_KEY')
# coincida EXACTAMENTE con el nombre que usaste en tu archivo .env
api_key = os.getenv("GEMINI_API_KEY")

# --- Paso 3: Verificar si la clave se cargó correctamente (para depuración) ---
if not api_key:
    st.error("Error: No se encontró la clave API de Gemini en las variables de entorno. Asegúrate de tener un archivo .env y la variable GEMINI_API_KEY configurada.")
    st.stop() # Detiene la ejecución de la app si no hay clave

# --- Paso 4: Configurar la API de Gemini con la clave obtenida ---
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- Datos de Seguros (preparados por el Maestro de Contenido) ---
# Simulación: en una app real, podrías cargar esto desde un CSV, JSON, o una base de datos.
# Para el hackathon, tenerlo directamente en el código o en un archivo .py separado es práctico.
DATOS_SEGUROS_VIDA = [
    {
        "nombre": "Póliza SeguraVida Clásica",
        "aseguradora": "GlobalProtect S.A.",
        "tipo": "Vida Entera",
        "beneficios": "Cobertura vitalicia, acumula valor en efectivo garantizado, elegible para dividendos.",
        "condiciones": "Edad de contratación 18-65 años, requiere examen médico, primas fijas.",
        "costo_ejemplo": "USD 80/mes (para persona de 30 años, no fumadora)",
        "ideal_para": "Personas que buscan cobertura permanente, ahorro a largo plazo, planificación patrimonial."
    },
    {
        "nombre": "Plan Futuro Brillante",
        "aseguradora": "AseguraMás Vida",
        "tipo": "Término (20 años)",
        "beneficios": "Cobertura por 20 años, prima baja, posibilidad de conversión a vida entera.",
        "condiciones": "Edad de contratación 20-55 años, posible examen médico simplificado, primas fijas durante el término.",
        "costo_ejemplo": "USD 35/mes (para persona de 30 años, no fumadora)",
        "ideal_para": "Familias jóvenes con hijos pequeños, personas con hipotecas, aquellos que necesitan cobertura por un período específico."
    },
    {
        "nombre": "Seguro Legado Duradero",
        "aseguradora": "Patrimonio Seguro",
        "tipo": "Vida Entera (con beneficios acelerados)",
        "beneficios": "Cobertura vitalicia, valor en efectivo, acceso anticipado a beneficios en caso de enfermedad terminal.",
        "condiciones": "Edad de contratación 25-60 años, examen médico, primas fijas.",
        "costo_ejemplo": "USD 100/mes (para persona de 30 años, no fumadora)",
        "ideal_para": "Quienes buscan seguridad a largo plazo y protección adicional ante enfermedades graves."
    },
    {
        "nombre": "Cobertura Express",
        "aseguradora": "Protección Rápida",
        "tipo": "Término (10 años)",
        "beneficios": "Proceso de aplicación rápido, sin examen médico (hasta cierto monto), cobertura básica por 10 años.",
        "condiciones": "Edad de contratación 20-50 años, primas fijas, límite de cobertura.",
        "costo_ejemplo": "USD 25/mes (para persona de 30 años, no fumadora)",
        "ideal_para": "Quienes necesitan cobertura rápida y básica, sin complicaciones."
    }
]

# --- Interfaz de Usuario en Streamlit ---
st.set_page_config(layout="wide")
st.title("🛡️ Comparador Inteligente de Seguros de Vida")
st.write("Encuentra la póliza que mejor se adapta a tus necesidades con la ayuda de la IA.")

st.header("1. Tus Requerimientos")
edad = st.slider("Tu edad", 18, 80, 30)
ingresos_anuales = st.number_input("Ingresos anuales estimados (USD)", min_value=0, value=30000, step=5000)
duracion_cobertura = st.selectbox(
    "¿Por cuánto tiempo deseas la cobertura?",
    ["Corta (ej. 10-20 años)", "Larga (ej. 30+ años o de por vida)", "No estoy seguro"]
)
prioridades = st.multiselect(
    "¿Qué es lo más importante para ti en un seguro de vida?",
    ["Costo bajo", "Cobertura de por vida", "Acumulación de valor en efectivo", "Proceso rápido", "Protección ante enfermedades graves", "Flexibilidad"]
)
comentarios_adicionales = st.text_area("¿Algún comentario adicional o necesidad específica?", "")

if st.button("Encontrar Mi Seguro Ideal"):
    # --- Construcción del Prompt Dinámico ---
    prompt_part_1_rol_y_directrices = """
    Eres un asistente de IA experto y neutral en seguros de vida. Tu tarea es analizar los requerimientos de un cliente y la información de varias pólizas de seguro de vida disponibles para recomendar la MEJOR OPCIÓN que se ajuste a sus necesidades.

    **Directrices para la Recomendación:**
    1.  Prioriza la opción que más se alinee con las necesidades explícitas del cliente (prioridades, duración, edad, ingresos).
    2.  Si hay varias opciones buenas, puedes mencionar la siguiente mejor alternativa.
    3.  Sé claro y conciso en la recomendación.
    4.  Explica por qué la póliza recomendada es la mejor opción para el cliente.
    5.  Siempre finaliza tu respuesta con una recomendación de que el cliente debe consultar con un asesor financiero certificado antes de tomar cualquier decisión.
    6.  No inventes información sobre seguros no listados.
    7.  Si no hay un ajuste claro, menciona la póliza más cercana y las razones, o indica que las opciones disponibles podrían no ajustarse perfectamente.
    """

    # Convertir los datos de seguros a un formato legible para el prompt
    seguros_disponibles_texto = "\n\n--- Seguros de Vida Disponibles ---\n"
    for seguro in DATOS_SEGUROS_VIDA:
        seguros_disponibles_texto += (
            f"**Nombre:** {seguro['nombre']}\n"
            f"**Aseguradora:** {seguro['aseguradora']}\n"
            f"**Tipo:** {seguro['tipo']}\n"
            f"**Beneficios Clave:** {seguro['beneficios']}\n"
            f"**Condiciones Principales:** {seguro['condiciones']}\n"
            f"**Costo Ejemplo:** {seguro['costo_ejemplo']}\n"
            f"**Ideal Para:** {seguro['ideal_para']}\n"
            f"-----------------------------------\n"
        )

    # Requerimientos del cliente
    requerimientos_cliente_texto = f"""
    --- Requerimientos del Cliente ---
    **Edad:** {edad} años
    **Ingresos Anuales:** USD {ingresos_anuales}
    **Duración de Cobertura Deseada:** {duracion_cobertura}
    **Prioridades Clave:** {', '.join(prioridades) if prioridades else 'No especificadas'}
    **Comentarios Adicionales:** {comentarios_adicionales if comentarios_adicionales else 'Ninguno'}
    """

    # Tarea específica y formato de salida
    prompt_part_final_tarea = """
    Analiza cuidadosamente los "Seguros de Vida Disponibles" y los "Requerimientos del Cliente". Basado en esta información, selecciona LA MEJOR opción de seguro de vida para este cliente y justifica tu elección.

    **Formato de Respuesta Deseado:**
    ---
    ### ✨ Tu Recomendación Personalizada: [Nombre del Seguro Recomendado]

    **Aseguradora:** [Nombre de la Aseguradora]
    **Tipo de Póliza:** [Tipo de póliza (Ej. Vida Entera, Término)]

    **✅ Por qué este seguro es ideal para ti:**
    [Explicación detallada de 2-3 puntos clave que conecten las necesidades del cliente con los beneficios del seguro.]

    **🔍 Puntos Clave a Considerar:**
    [Resume brevemente los principales beneficios y condiciones del seguro.]

    **💰 Costo Ejemplo:** [Costo estimado del seguro]

    ---
    **Importante:** Recuerda que esta es una recomendación basada en la información proporcionada. Te recomendamos encarecidamente **consultar a un asesor financiero certificado** para obtener un análisis personalizado y asegurarte de que la póliza se adapte perfectamente a tu situación específica.
    """

    # Unir todas las partes para formar el prompt completo
    full_prompt = (
        prompt_part_1_rol_y_directrices +
        seguros_disponibles_texto +
        requerimientos_cliente_texto +
        prompt_part_final_tarea
    )
    
    st.markdown("---")
    st.subheader("Buscando tu seguro ideal...")
    
    try:
        response = model.generate_content(full_prompt)
        st.write(response.text) # Muestra la respuesta formateada por Gemini
    except Exception as e:
        st.error(f"¡Oops! Hubo un error al buscar tu seguro: {e}. Por favor, inténtalo de nuevo más tarde.")
        st.info("Asegúrate de que tu clave API de Gemini sea correcta y que tengas conexión a internet.")