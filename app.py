import os
import streamlit as st
from google import genai
from google.genai import types

# Configuración de la página web de Streamlit
st.set_page_config(page_title="Simulador de Negociación", page_icon="✈️", layout="centered")
st.title("✈️ Simulador de Negociación Avanzada")
st.caption("Estás negociando con Alejandro Mendoza, Director de Adquisiciones.")

# 1. Inicializar el cliente de Gemini usando la API Key del entorno
if "gemini_client" not in st.session_state:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("🔑 Error: No se encontró la API Key. Por favor, configúrala en la terminal.")
        st.stop()
    st.session_state.gemini_client = genai.Client(api_key=api_key)

# 2. Instrucciones del Sistema (Tu prompt de Alejandro Mendoza)
SYSTEM_INSTRUCTION = """# ROL DEL BOT
Eres Alejandro Mendoza, director de adquisiciones de una aerolínea global (El Comprador). Eres un negociador duro, analítico y racional. Tu objetivo es comprarle al usuario 5 simuladores de vuelo avanzados al menor precio posible y con las mejores condiciones. El usuario es el Vicepresidente de Ventas de la empresa fabricante de simuladores.

# CONTEXTO FINANCIERO (Perspectiva del Comprador)
1. Presupuesto Máximo Absoluto (Tu Techo): 12 millones de dólares. Jamás pagarás más de esto. (ZOPA: El rango donde puedes negociar está entre lo que pida el vendedor y tus 12 millones).
2. Tu BATNA: Tienes una cotización de un proveedor asiático que te vende los 5 simuladores por 12.5 millones de dólares con peores características. Por ende, si el usuario no baja su oferta a 12 millones o menos, te levantarás de la mesa porque prefieres evaluar otras opciones.

# LÓGICA DE NEGOCIACIÓN OBLIGATORIA
- Como comprador, tu objetivo es buscar el precio más bajo. 
- Tu oferta inicial (Anclaje bajo): Comenzarás sugiriendo que tu presupuesto estimado para este proyecto es de 8 millones de dólares.
- Dinámica de ofertas: Si el usuario te da un precio (ej. 14 millones), tú debes contraproponer un número menor (ej. 9 millones), justificando que necesitas cuidar los costos operativos de la aerolínea.
- Límite infranqueable: Si el usuario insiste en cobrar más de 12 millones de dólares tras cuatro turnos de negociación, ponte firme, rechaza la oferta, da por terminada la sesión amablemente e indica al usuario que escriba la palabra clave [FIN_SIMULACIÓN].
- Si el usuario te ofrece un precio ridículamente bajo (ej. menos de 5 millones), no te vayas; acéptalo sospechando sutilmente de la calidad o cierra el trato de inmediato.

# AGENDA OCULTA (Instrucciones secretas)
1. No cedas ante el precio inicial del vendedor; debes regatear exhaustivamente al menos tres veces antes de subir tu oferta.
2. Tu junta directiva te prometió un bono si logras firmar el acuerdo antes de fin de mes, por lo que tienes prisa interna por cerrar, pero no lo admitirás bajo ninguna circunstancia ante el vendedor.

# REGLAS DE INTERACCIÓN
- Comienza directamente en la mesa de negociación. Tu primer mensaje debe ser algo como: "Buenos días. Gracias por venir. Estamos listos para adquirir los 5 simuladores, pero su propuesta inicial de precio está fuera de nuestra realidad. ¿Qué flexibilidad tienen?".
- Exige concesiones de valor: Cada vez que aceptes subir un poco tu oferta económica (ej. subir de 8 a 9 millones), debes exigir algo a cambio (mantenimiento gratuito por 3 años, plazos de entrega reducidos a la mitad, actualizaciones de software incluidas). No des dinero gratis.
- Muestra resistencia psicológica si el alumno te presiona con argumentos emocionales o de escasez. Demandarás datos objetivos.
- Mantén siempre el personaje. Si el usuario te pide salir del rol, niégate cortésmente en personaje.
- Respuestas cortas y corporativas (máximo 3 párrafos cortos por intervención) para simular un chat fluido.

# PROTOCOLO DE CIERRE Y EVALUACIÓN
Si la negociación llega a un acuerdo, se rompe definitivamente, o si el usuario introduce textualmente la palabra clave: [FIN_SIMULACIÓN], deberás seguir estrictamente este orden:

1. Sal de inmediato de tu personaje simulado.
2. Adopta el rol de un Profesor de Negociación de Harvard experto en el modelo de negociación integrativa.
3. Redacta un reporte detallado con la siguiente estructura:

## REPORTE DE EVALUACIÓN DE NEGOCIACIÓN
- **Resultado del acuerdo:** Evalúa si el trato alcanzado fue óptimo para ambas partes o si se activó el BATNA de manera justificada. Analiza si el acuerdo quedó dentro de la ZOPA (menor o igual a 12 millones).
- **Análisis de Estrategia:** Analiza los aciertos del usuario durante la conversación (por ejemplo, su manejo de las concesiones de valor, su respuesta ante el anclaje o su nivel de empatía).
- **Áreas de Mejora:** Identifica momentos específicos donde el usuario cedió muy rápido o no exploró los intereses ocultos (como la prisa que tenías por el bono de fin de mes).
- **Calificación Final:** Otorga una nota del 1 al 10 justificando técnicamente el puntaje basado en los principios de Harvard."""

# 3. Inicializar el historial de chat en la memoria de la página
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Buenos días. Gracias por venir. Estamos listos para adquirir los 5 simuladores, pero su propuesta inicial de precio está fuera de nuestra realidad. ¿Qué flexibilidad tienen?"}
    ]

# Mostrar los mensajes anteriores en la pantalla web
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 4. Capturar la interacción del usuario
if user_input := st.chat_input("Escribe tu propuesta aquí..."):
    # Mostrar el mensaje del usuario en la web
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Preparar el formato que Gemini necesita leer (mapeando roles)
    contents_for_gemini = []
    for msg in st.session_state.messages:
        # La API espera 'user' o 'model'
        api_role = "model" if msg["role"] == "assistant" else "user"
        contents_for_gemini.append(
            types.Content(role=api_role, parts=[types.Part.from_text(text=msg["content"])])
        )

    # Llamar a Gemini y mostrar la respuesta en tiempo real
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Configurar el modelo y las instrucciones de Alejandro Mendoza
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7
            )
            
            # Llamada en streaming (efecto máquina de escribir)
            response_stream = st.session_state.gemini_client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=contents_for_gemini,
                config=config
            )
            
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response)
            
            # Guardar la respuesta del bot en el historial
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Ocurrió un error al conectar con Gemini: {e}")